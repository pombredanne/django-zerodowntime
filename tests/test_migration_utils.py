from collections import OrderedDict

from django.apps import apps
from django.conf import settings
from django.db import DEFAULT_DB_ALIAS, connections, models
from django.db.migrations import operations
from django.test import TestCase

from zerodowntime import migration_utils


class MigrationUtilsTestCase(TestCase):
    def setUp(self):
        settings.INSTALLED_APPS = [
            'zerodowntime',
            'tests.safe_migrations',
        ]

        self.reinitialize_django_apps()

    def test_operation_is_safe(self):
        assert migration_utils.operation_is_safe(operations.AddField(
            model_name='unsafemodel',
            name='safe_field',
            field=models.IntegerField(null=True),
        ))

        assert migration_utils.operation_is_safe(operations.AddField(
            model_name='unsafemodel',
            name='field_added',
            field=models.IntegerField(default=1),
            preserve_default=False,
        )) is False

        assert migration_utils.operation_is_safe(operations.AlterField(
            model_name='unsafemodel',
            name='field_added',
            field=models.PositiveIntegerField(default=10),
            preserve_default=False
        )) is False

        assert migration_utils.operation_is_safe(operations.RenameField(
            model_name='unsafemodel',
            old_name='field_added',
            new_name='field_renamed'
        )) is False

        assert migration_utils.operation_is_safe(operations.RemoveField(
            model_name='unsafemodel',
            name='field_renamed',
        )) is False

        assert migration_utils.operation_is_safe(operations.DeleteModel('unsafemodel')) is False

        assert migration_utils.operation_is_safe(operations.RunSQL("")) is False
        assert migration_utils.operation_is_safe(operations.RunPython(lambda: True)) is False

    def test_find_unsafe_migrations(self):
        conn = connections[DEFAULT_DB_ALIAS]
        result = migration_utils.find_unsafe_migrations(conn)

        assert len(result) == 0

        self.add_django_app('tests.unsafe_migrations')

        result = migration_utils.find_unsafe_migrations(conn)
        assert len(result) == 2

        unsafemodel_field_added = result[0]
        assert unsafemodel_field_added.app_name == 'unsafe_migrations'
        assert unsafemodel_field_added.migration_name == '0002_unsafemodel_field_added'
        assert len(unsafemodel_field_added.offending_operations) == 1

        unsafemodel_kitchen_sink = result[1]
        assert unsafemodel_kitchen_sink.app_name == 'unsafe_migrations'
        assert unsafemodel_kitchen_sink.migration_name == '0003_unsafemodel_kitchen_sink'
        assert len(unsafemodel_kitchen_sink.offending_operations) == 5

    def test_find_migration_conflicts(self):
        conn = connections[DEFAULT_DB_ALIAS]
        self.add_django_app('tests.conflicting_migrations')

        result = migration_utils.find_unsafe_migrations(conn)

        assert result[0].app_name == 'conflicting_migrations'
        assert result[0].migration_names == {
            '0002_unsafemodel_some_other_changes',
            '0002_unsafemodel_first_changes'
        }

    def add_django_app(self, app_module):
        settings.INSTALLED_APPS.append(app_module)
        self.reinitialize_django_apps()

    def reinitialize_django_apps(self):
        apps.app_configs = OrderedDict()
        # set ready to false so that populate will work
        apps.ready = False
        # re-initialize them all; is there a way to add just one without reloading them all?
        apps.populate(settings.INSTALLED_APPS)
