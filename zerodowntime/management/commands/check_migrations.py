from django.core.management import BaseCommand
from django.db import DEFAULT_DB_ALIAS
from django.db import connections

from zerodowntime.migration_utils import UnsafeMigration, find_unsafe_migrations


class Command(BaseCommand):
    help = 'Analyzes pending migrations to determine whether or not they are compatible with a' \
           'zero-downtime continuous delivery deployment.'

    def handle(self, *args, **options):
        connection = connections[DEFAULT_DB_ALIAS]

        unsafe_migrations = find_unsafe_migrations(connection)

        if len(unsafe_migrations) > 0:
            self.print_error_report(unsafe_migrations)

            exit(len(unsafe_migrations))

    # noinspection PyMethodMayBeStatic
    def print_error_report(self, unsafe_migrations):
        print("These operations are incompatible with Zero Downtime Deployments:")

        for migration in unsafe_migrations:
            assert isinstance(migration, UnsafeMigration)

            print("\n\n{}.{}:".format(migration.app_name, migration.migration_name))

            print('\tOPERATIONS:')
            print('\t-----------')
            for operation in migration.offending_operations:
                print('\t* ', operation.describe())

            print()

            print('\tSQL STATEMENTS:')
            print('\t---------------')
            for statement in migration.sql_statements:
                print('\t{}'.format(statement))

            print()
