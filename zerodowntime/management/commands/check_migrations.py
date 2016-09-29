from django.core.management import BaseCommand
from django.db import connections

from zerodowntime.migration_utils import MigrationConflict, UnsafeMigration, find_unsafe_migrations


def print_unsafe_migration(migration):
    print("\n\n{}.{}:".format(migration.app_name, migration.migration_name))
    print('\tOPERATIONS:')
    print('\t-----------')

    for operation in migration.offending_operations:
        print('\t* ', operation.describe())

    print('\n\tSQL STATEMENTS:')
    print('\t---------------')

    for statement in migration.sql_statements:
        print('\t{}'.format(statement))

    print('\n')


def print_migration_conflict(migration):
    print("\n\nMigration Conflict found in app: {app}, migrations: {migrations}:".format(
        app=migration.app_name,
        migrations=migration.migration_name
    ))


class Command(BaseCommand):
    help = 'Analyzes pending migrations to determine whether or not they are compatible with a' \
           'zero-downtime continuous delivery deployment.'

    def handle(self, *args, **options):
        connection = connections['CHECK_MIGRATIONS']

        unsafe_migrations = find_unsafe_migrations(connection)

        if len(unsafe_migrations) > 0:
            self.print_error_report(unsafe_migrations)

            exit(len(unsafe_migrations))

    # noinspection PyMethodMayBeStatic
    def print_error_report(self, unsafe_migrations):
        print("These operations are incompatible with Zero Downtime Deployments:")

        for migration in unsafe_migrations:
            if isinstance(migration, UnsafeMigration):
                print_unsafe_migration(migration)
            elif isinstance(migration, MigrationConflict):
                print_migration_conflict(migration)
