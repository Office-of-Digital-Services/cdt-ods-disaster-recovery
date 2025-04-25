import os

import psycopg

from django.core.management.base import BaseCommand
from django.db import connections


class Command(BaseCommand):
    help = "Completely resets the database (DESTRUCTIVE)."

    def admin_connection(self) -> psycopg.Connection:
        db_host = connections["default"].settings_dict["HOST"]
        db_port = connections["default"].settings_dict["PORT"]

        postgres_db = os.environ.get("POSTGRES_DB", "postgres")
        admin_name = os.environ.get("POSTGRES_USER", "postgres")
        admin_password = os.environ.get("POSTGRES_PASSWORD")

        if not admin_password:
            self.stderr.write(self.style.ERROR("POSTGRES_PASSWORD environment variable not set"))
            return

        return psycopg.connect(
            host=db_host,
            port=db_port,
            user=admin_name,
            password=admin_password,
            dbname=postgres_db,
            # Execute SQL commands immediately
            autocommit=True,
        )

    def reset_db(self, db_name, db_user, db_password):
        try:
            with self.admin_connection() as conn:
                cursor = conn.cursor()
                self.stdout.write(self.style.WARNING("Attempting database reset..."))

                # Revoke existing connections
                cursor.execute(
                    """
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE datname = %s AND pg_stat_activity.pid <> pg_backend_pid()
                    """,
                    [db_name],
                )
                self.stdout.write(self.style.SUCCESS(f"Terminated existing connections to '{db_name}'"))

                # Drop database
                cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
                self.stdout.write(self.style.SUCCESS(f"Database '{db_name}' dropped."))

                # Create Django user
                cursor.execute(f"DROP USER IF EXISTS {db_user}")
                cursor.execute(f"CREATE USER {db_user} WITH PASSWORD '{db_password}'")
                self.stdout.write(self.style.SUCCESS(f"Django user '{db_user}' created"))

                # Create Django database with Django user as owner
                cursor.execute(f"CREATE DATABASE {db_name} WITH OWNER {db_user} ENCODING 'UTF-8'")
                self.stdout.write(self.style.SUCCESS(f"Database '{db_name}' created and owned by '{db_user}'"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error during database reset: {e}"))

    def handle(self, *args, **options):
        for db in connections:
            db_name = connections[db].settings_dict["NAME"]
            db_user = connections[db].settings_dict["USER"]
            db_password = connections[db].settings_dict["PASSWORD"]

            if not db_password:
                self.stderr.write(self.style.ERROR(f"Password for db '{db}' not set"))
                return

            self.reset_db(db_name, db_user, db_password)
