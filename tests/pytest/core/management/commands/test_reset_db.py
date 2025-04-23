import pytest

from web.core.management.commands import reset_db


@pytest.fixture
def command(mocker):
    cmd = reset_db.Command()
    # mocking command I/O for tests
    cmd.stderr = mocker.Mock()
    cmd.stdout = mocker.Mock()
    cmd.style.ERROR = str
    cmd.style.SUCCESS = str
    cmd.style.WARNING = str
    return cmd


@pytest.fixture(autouse=True)
def db_settings(settings):
    settings.DATABASES["default"]["NAME"] = "test_db"
    settings.DATABASES["default"]["USER"] = "test_user"
    settings.DATABASES["default"]["PASSWORD"] = "test_password"
    settings.DATABASES["default"]["HOST"] = "test_host"
    settings.DATABASES["default"]["PORT"] = "1234"
    return settings


@pytest.fixture
def mock_connect(mocker):
    mock = mocker.patch.object(reset_db.psycopg, "connect", mocker.Mock())
    return mock


@pytest.fixture
def mock_cursor(mocker):
    return mocker.Mock()


@pytest.fixture
def mock_conn(mocker, mock_cursor):
    mock = mocker.MagicMock()
    # fake context manager support for `with manager() as ctx:`
    mock.__enter__.return_value = mock
    mock.cursor.return_value = mock_cursor
    return mock


@pytest.fixture
def mock_admin_connection(mocker, mock_conn):
    return mocker.patch.object(reset_db.Command, "admin_connection", return_value=mock_conn)


@pytest.mark.django_db
class TestCommand:
    @pytest.mark.parametrize(
        "env_vars,should_connect",
        [
            ({"POSTGRES_DB": "test_db", "POSTGRES_USER": "test_user", "POSTGRES_PASSWORD": "test_pass"}, True),
            ({"POSTGRES_DB": "test_db", "POSTGRES_USER": "test_user", "POSTGRES_PASSWORD": ""}, False),
        ],
    )
    def test_admin_connection(self, command: reset_db.Command, monkeypatch, mock_connect, env_vars, should_connect):
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        result = command.admin_connection()

        if should_connect:
            mock_connect.assert_called_once_with(
                host="test_host", port="1234", user="test_user", password="test_pass", dbname="test_db", autocommit=True
            )
            assert result is not None
        else:
            assert result is None

    def test_handle_success(self, command: reset_db.Command, mocker, mock_admin_connection, mock_cursor):
        mocker.patch("os.environ.get", return_value="test_password")

        command.handle()

        mock_admin_connection.assert_called_once()
        assert mock_cursor.execute.call_count == 5

        # Verify success messages were logged
        expected_messages = [
            "Attempting database reset...",
            "Terminated existing connections to 'test_db'.",
            "Database 'test_db' dropped.",
            "Django user 'test_user' created.",
            "Database 'test_db' created and owned by 'test_user'.",
            "Database reset and user setup complete.",
        ]

        for message in expected_messages:
            command.stdout.write.assert_any_call(message)

    def test_handle_no_db_password(self, command: reset_db.Command, db_settings, mock_admin_connection):
        db_settings.DATABASES["default"]["PASSWORD"] = None

        command.handle()

        mock_admin_connection.assert_not_called()
        command.stderr.write.assert_any_call("DJANGO_DB_PASSWORD environment variable not set.")

    def test_handle_admin_connection_error(self, command: reset_db.Command, mock_admin_connection):
        mock_admin_connection.side_effect = Exception("Admin connection failed.")

        command.handle()

        mock_admin_connection.assert_called_once()
        command.stderr.write.assert_any_call("Error during database reset: Admin connection failed.")
