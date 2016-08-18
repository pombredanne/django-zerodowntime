import operator
from collections import namedtuple
from typing import List

from django.db.migrations import Migration, operations
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.state import ProjectState
from django.db.models import NOT_PROVIDED

SAFE_OPERATIONS = (
    operations.CreateModel,
    operations.AddField,
    operations.AlterModelOptions,
)

UnsafeMigration = namedtuple('UnsafeMigration', (
    'app_name', 'migration_name', 'offending_operations', 'sql_statements'
))


def analyze_migration(connection, migration, project_state):
    unsafe_operations = []

    for operation in migration.operations:
        if not operation_is_safe(operation):
            unsafe_operations.append(operation)

    if len(unsafe_operations) > 0:
        sql_statements = extract_sql_statements(connection, migration, project_state)

        return UnsafeMigration(migration.app_label, migration.name, unsafe_operations, sql_statements)


def extract_sql_statements(connection, migration, project_state):
    schema_editor = connection.schema_editor(collect_sql=True)
    schema_editor.deferred_sql = []
    schema_editor.skip_default = lambda x: True

    migration.apply(project_state, schema_editor, collect_sql=True)

    return schema_editor.collected_sql + schema_editor.deferred_sql


def operation_is_safe(operation):
    if not isinstance(operation, SAFE_OPERATIONS):
        return False
    elif isinstance(operation, (operations.AddField, operations.AlterField)):
        if operation.field.null is False or operation.field.default is not NOT_PROVIDED:
            return False

    return True


def find_unsafe_migrations(connection):
    loader = MigrationLoader(connection)

    disk_migrations = set(loader.disk_migrations.keys())
    new_migrations = disk_migrations.difference(loader.applied_migrations)

    unsafe_migrations = []
    for app_name, migration_name in new_migrations:
        migration = loader.get_migration(app_name, migration_name)
        project_state = loader.project_state((app_name, migration_name), at_end=False)

        result = analyze_migration(connection, migration, project_state)
        if result:
            unsafe_migrations.append(result)

    unsafe_migrations = sorted(unsafe_migrations, key=operator.attrgetter('app_name', 'migration_name'))

    return unsafe_migrations
