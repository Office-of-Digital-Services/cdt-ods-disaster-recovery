import psycopg
import pytest
from django.core.management.base import CommandError
from django.db import DEFAULT_DB_ALIAS

from web.core.management.commands.ensure_db import Command


@pytest.fixture
def command(mocker):
    """Provides an instance of the Command, with stdout/stderr mocked."""
    cmd = Command()
    cmd.stdout.write = mocker.MagicMock()
    cmd.stderr.write = mocker.MagicMock()
    return cmd


@pytest.fixture
def mock_call_command(mocker):
    return mocker.patch("web.core.management.commands.ensure_db.call_command")


@pytest.fixture
def mock_get_user_model(mocker):
    MockUser = mocker.MagicMock()
    MockUser.objects.using(DEFAULT_DB_ALIAS).filter.return_value.exists.return_value = False
    return mocker.patch("web.core.management.commands.ensure_db.get_user_model", return_value=MockUser)


def test_admin_connection_success(command, mock_psycopg_connect, mock_admin_connection, mock_os_environ, settings):
    mock_psycopg_connect.return_value = mock_admin_connection
    settings.DATABASES = {
        DEFAULT_DB_ALIAS: {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": "test_db_host",
            "PORT": "1234",
        }
    }
    mock_os_environ["POSTGRES_PASSWORD"] = "pg_super_secret"
    mock_os_environ["POSTGRES_USER"] = "pg_admin_user"
    mock_os_environ["POSTGRES_DB"] = "pg_maintenance_db"

    conn = command._admin_connection()

    mock_psycopg_connect.assert_called_once_with(
        host="test_db_host",
        port="1234",
        user="pg_admin_user",
        password="pg_super_secret",
        dbname="pg_maintenance_db",
        autocommit=True,
    )
    assert conn == mock_admin_connection


def test_admin_connection_no_postgres_password(command, mock_os_environ, settings):
    settings.DATABASES = {DEFAULT_DB_ALIAS: {"HOST": "db", "PORT": "5432"}}
    mock_os_environ.pop("POSTGRES_PASSWORD", None)

    with pytest.raises(
        CommandError, match="POSTGRES_PASSWORD environment variable not set. Cannot establish admin connection."
    ):
        command._admin_connection()


def test_admin_connection_psycopg_error(command, mock_psycopg_connect, mock_os_environ, settings):
    settings.DATABASES = {DEFAULT_DB_ALIAS: {"HOST": "db", "PORT": "5432"}}
    mock_os_environ["POSTGRES_PASSWORD"] = "pg_super_secret"
    mock_psycopg_connect.side_effect = psycopg.OperationalError("DB connection failed")

    with pytest.raises(CommandError, match="Admin connection to PostgreSQL failed: DB connection failed"):
        command._admin_connection()


DB_TEST_ALIAS = "testdb"  # Define a clear alias for these tests


def test_ensure_users_and_db_creates_new_user_and_db(command, mock_admin_connection, mock_psycopg_cursor, settings):
    db_config = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "example_db",
        "USER": "example_user",
        "PASSWORD": "example_password",
    }
    settings.DATABASES = {DB_TEST_ALIAS: db_config}
    mock_psycopg_cursor.fetchone.side_effect = [None, None, (1,)]  # User not exist, DB not exist, User exists for owner check

    command._ensure_users_and_db(mock_admin_connection)

    execute_calls = mock_psycopg_cursor.execute.call_args_list
    create_user_call = next(c for c in execute_calls if "CREATE USER" in str(c.args[0]))
    assert db_config["USER"] in str(create_user_call.args[0])
    assert create_user_call.args[1] == [db_config["PASSWORD"]]

    create_db_call = next(c for c in execute_calls if "CREATE DATABASE" in str(c.args[0]))
    assert db_config["NAME"] in str(create_db_call.args[0])
    assert db_config["USER"] in str(create_db_call.args[0])  # Owner
    assert create_db_call.args[1] == ["UTF-8"]  # Encoding

    command.stdout.write.assert_any_call(f"User: {db_config['USER']} for database: {DB_TEST_ALIAS} not found. Creating...")
    command.stdout.write.assert_any_call(
        command.style.SUCCESS(f"User: {db_config['USER']} for database: {DB_TEST_ALIAS} created successfully")
    )
    command.stdout.write.assert_any_call(f"Database {db_config['NAME']} not found. Creating...")
    command.stdout.write.assert_any_call(
        command.style.SUCCESS(f"Database {db_config['NAME']} with owner {db_config['USER']} created successfully")
    )
    mock_psycopg_cursor.close.assert_called_once()


def test_ensure_users_and_db_user_exists_db_not_exists(command, mock_admin_connection, mock_psycopg_cursor, settings):
    db_config = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "another_example_db",
        "USER": "current_user",
        "PASSWORD": "pwd123",
    }
    settings.DATABASES = {DB_TEST_ALIAS: db_config}
    mock_psycopg_cursor.fetchone.side_effect = [(1,), None, (1,)]  # User exists, DB not exist, User exists for owner check

    command._ensure_users_and_db(mock_admin_connection)

    assert not any("CREATE USER" in str(call.args[0]) for call in mock_psycopg_cursor.execute.call_args_list)
    assert any("CREATE DATABASE" in str(call.args[0]) for call in mock_psycopg_cursor.execute.call_args_list)
    command.stdout.write.assert_any_call(f"User found: {db_config['USER']}")
    command.stdout.write.assert_any_call(f"Database {db_config['NAME']} not found. Creating...")


def test_ensure_users_and_db_skips_non_postgres(command, mock_admin_connection, mock_psycopg_cursor, settings):
    db_alias_sqlite = "sqlite_db"
    settings.DATABASES = {
        DB_TEST_ALIAS: {"ENGINE": "django.db.backends.postgresql", "NAME": "db1", "USER": "u1", "PASSWORD": "p1"},
        db_alias_sqlite: {"ENGINE": "django.db.backends.sqlite3", "NAME": "test.db"},
    }
    mock_psycopg_cursor.fetchone.return_value = (1,)  # Assume PG db and user exist

    command._ensure_users_and_db(mock_admin_connection)

    command.stdout.write.assert_any_call(
        command.style.WARNING(f"Skipping database {db_alias_sqlite}, ENGINE is not PostgreSQL.")
    )
    command.stdout.write.assert_any_call(f"Database configuration: {DB_TEST_ALIAS}")


def test_ensure_users_and_db_incomplete_config(command, mock_admin_connection, settings):
    settings.DATABASES[DB_TEST_ALIAS] = {"ENGINE": "django.db.backends.postgresql", "NAME": "db1"}  # Missing USER/PASSWORD

    command._ensure_users_and_db(mock_admin_connection)

    command.stderr.write.assert_any_call(
        command.style.ERROR(
            f"Skipping database {DB_TEST_ALIAS} with incomplete configuration (missing NAME, USER, or PASSWORD)."
        )
    )


def test_ensure_users_and_db_user_creation_fails(command, mocker, mock_admin_connection, mock_psycopg_cursor, settings):
    db_config = {"ENGINE": "django.db.backends.postgresql", "NAME": "fail_db", "USER": "fail_user", "PASSWORD": "fp"}
    settings.DATABASES = {DB_TEST_ALIAS: db_config}
    mock_psycopg_cursor.fetchone.return_value = None

    error_on_create = psycopg.ProgrammingError("Cannot create this specific user")

    def execute_side_effect(sql_query, params=None):
        if "CREATE USER" in str(sql_query) and db_config["USER"] in str(sql_query):
            raise error_on_create
        m = mocker.MagicMock()
        m.fetchone.return_value = None
        return m

    mock_psycopg_cursor.execute.side_effect = execute_side_effect

    with pytest.raises(psycopg.ProgrammingError):
        command._ensure_users_and_db(mock_admin_connection)


def test_ensure_users_and_db_creation_fails_owner_missing(
    command, mocker, mock_admin_connection, mock_psycopg_cursor, settings
):
    db_config = {"ENGINE": "django.db.backends.postgresql", "NAME": "ownerless_db", "USER": "ghost_user", "PASSWORD": "gp"}
    settings.DATABASES = {DB_TEST_ALIAS: db_config}
    mock_psycopg_cursor.fetchone.side_effect = [None, None, None]  # User not found, DB not found, Owner (user) not found

    original_execute = mock_psycopg_cursor.execute

    def permissive_create_user_execute(sql_query, params=None):
        if "CREATE USER" in str(sql_query):
            return mocker.MagicMock()
        return original_execute(sql_query, params)

    mock_psycopg_cursor.execute = permissive_create_user_execute

    command._ensure_users_and_db(mock_admin_connection)

    command.stderr.write.assert_any_call(
        command.style.ERROR(
            f"Cannot create database: {db_config['NAME']} because user: {db_config['USER']} does not exist or was not created"
        )
    )


def test_run_migrations_success(command, mock_call_command, settings):
    settings.DATABASES = {
        DEFAULT_DB_ALIAS: {"ENGINE": "django.db.backends.postgresql", "NAME": "db1", "USER": "u1", "PASSWORD": "p1"}
    }

    command._run_migrations()

    mock_call_command.assert_called_once_with("migrate", database=DEFAULT_DB_ALIAS, interactive=False)
    command.stdout.write.assert_any_call(command.style.SUCCESS(f"Migrations complete for database: {DEFAULT_DB_ALIAS}"))


def test_run_migrations_multiple_dbs(command, mock_call_command, settings):
    settings.DATABASES = {
        DEFAULT_DB_ALIAS: {"ENGINE": "django.db.backends.postgresql", "NAME": "db1", "USER": "u1", "PASSWORD": "p1"},
        "tasks_db": {"ENGINE": "django.db.backends.postgresql", "NAME": "tasks", "USER": "u2", "PASSWORD": "p2"},
        "other_db": {"ENGINE": "django.db.backends.sqlite3", "NAME": "other"},
    }

    command._run_migrations()

    assert mock_call_command.call_count == 2
    mock_call_command.assert_any_call("migrate", database=DEFAULT_DB_ALIAS, interactive=False)
    mock_call_command.assert_any_call("migrate", database="tasks_db", interactive=False)
    command.stdout.write.assert_any_call(
        command.style.WARNING("Skipping migrations for database: other_db. ENGINE is not PostgreSQL.")
    )


def test_run_migrations_failure_raises_commanderror(command, mock_call_command, settings):
    db_alias_fail = DEFAULT_DB_ALIAS
    settings.DATABASES = {
        db_alias_fail: {"ENGINE": "django.db.backends.postgresql", "NAME": "db1", "USER": "u1", "PASSWORD": "p1"}
    }
    error_obj = Exception("Migration critical failure!")
    mock_call_command.side_effect = error_obj

    with pytest.raises(CommandError, match=f"Migration failed for {db_alias_fail}."):
        command._run_migrations()

    command.stderr.write.assert_any_call(f"Error running migrations for database: {db_alias_fail}")
    assert any(error_obj is call_arg.args[0] for call_arg in command.stderr.write.call_args_list if call_arg.args)


def test_ensure_superuser_creates_if_not_exists(command, mock_os_environ, mock_get_user_model, mock_call_command):
    username = "new_super_user"
    email = "new_super@example.com"
    mock_os_environ["DJANGO_SUPERUSER_USERNAME"] = username
    mock_os_environ["DJANGO_SUPERUSER_EMAIL"] = email
    mock_os_environ["DJANGO_SUPERUSER_PASSWORD"] = "super_password123"

    command._ensure_superuser()

    mock_get_user_model.return_value.objects.using(DEFAULT_DB_ALIAS).filter(username=username).exists.assert_called_once()
    mock_call_command.assert_called_once_with("createsuperuser", interactive=False, username=username, email=email)
    command.stdout.write.assert_any_call(f"Superuser: {username} not found. Creating in database: {DEFAULT_DB_ALIAS}...")


def test_ensure_superuser_already_exists(command, mock_os_environ, mock_get_user_model, mock_call_command):
    username = "current_super_user"
    mock_os_environ["DJANGO_SUPERUSER_USERNAME"] = username
    mock_get_user_model.return_value.objects.using(DEFAULT_DB_ALIAS).filter(username=username).exists.return_value = True

    command._ensure_superuser()

    command.stdout.write.assert_any_call(f"Superuser: {username} already exists in database: {DEFAULT_DB_ALIAS}")
    mock_call_command.assert_not_called()


def test_ensure_superuser_username_not_set(command, mock_os_environ, mock_call_command):
    command._ensure_superuser()

    command.stdout.write.assert_any_call(
        "DJANGO_SUPERUSER_USERNAME environment variable not set. Skipping superuser creation."
    )
    mock_call_command.assert_not_called()


def test_ensure_superuser_creation_missing_email_env_var(command, mock_os_environ, mock_get_user_model, mock_call_command):
    username = "incomplete_super"
    mock_os_environ["DJANGO_SUPERUSER_USERNAME"] = username
    mock_os_environ["DJANGO_SUPERUSER_PASSWORD"] = "super_password123"
    # mock_get_user_model has exists() returning False

    command._ensure_superuser()

    command.stdout.write.assert_any_call(
        command.style.WARNING(
            f"Cannot create superuser: {username}. DJANGO_SUPERUSER_EMAIL or DJANGO_SUPERUSER_PASSWORD environment variables are not set."  # noqa: E501
        )
    )
    mock_call_command.assert_not_called()


def test_handle_success_path(command, mocker):
    mock_conn_obj = mocker.MagicMock(spec=psycopg.Connection, closed=False)

    def mock_admin_conn_close():
        mock_conn_obj.closed = True

    mock_conn_obj.close = mock_admin_conn_close

    mocker.patch.object(command, "_admin_connection", return_value=mock_conn_obj)
    mocker.patch.object(command, "_ensure_users_and_db")
    mocker.patch.object(command, "_run_migrations")
    mocker.patch.object(command, "_ensure_superuser")

    command.handle()

    command._admin_connection.assert_called_once()
    command._ensure_users_and_db.assert_called_once_with(mock_conn_obj)
    command._run_migrations.assert_called_once()
    command._ensure_superuser.assert_called_once()
    assert mock_conn_obj.closed
    command.stdout.write.assert_any_call(command.style.SUCCESS("ensure_db command finished successfully."))


def test_handle_admin_connection_fails(command, mocker):
    admin_connect_error_msg = "Admin connection totally failed"
    mocker.patch.object(command, "_admin_connection", side_effect=CommandError(admin_connect_error_msg))
    mock_ensure_users_db = mocker.patch.object(command, "_ensure_users_and_db")
    mock_migrations = mocker.patch.object(command, "_run_migrations")
    mock_superuser = mocker.patch.object(command, "_ensure_superuser")

    command.handle()

    command._admin_connection.assert_called_once()
    command.stderr.write.assert_any_call(command.style.ERROR(admin_connect_error_msg))
    mock_ensure_users_db.assert_not_called()
    mock_migrations.assert_not_called()
    mock_superuser.assert_not_called()


def test_handle_run_migrations_fails(command, mocker):
    mock_conn_obj = mocker.MagicMock(spec=psycopg.Connection, closed=False)
    mock_conn_obj.close = mocker.MagicMock()
    mocker.patch.object(command, "_admin_connection", return_value=mock_conn_obj)
    mocker.patch.object(command, "_ensure_users_and_db")

    mocker.patch.object(command, "_run_migrations", side_effect=Exception())
    mock_superuser = mocker.patch.object(command, "_ensure_superuser")

    with pytest.raises(Exception):
        command.handle()

    mock_superuser.assert_not_called()
    mock_conn_obj.close.assert_called_once()
