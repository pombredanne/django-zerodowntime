import os
import shutil
import tempfile

from django.test import TestCase

from zerodowntime.management.commands import install_git_hooks


class MigrationUtilsTestCase(TestCase):
    def setUp(self):
        self.command = install_git_hooks.Command()
        self.command.HOOK_PATH = os.path.join(tempfile.gettempdir(), '.git/hooks')
        os.makedirs(self.command.HOOK_PATH, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.command.HOOK_PATH, True)

    def test_command_works_when_file_does_not_exist(self):
        self.command.handle()

        with open(os.path.join(self.command.HOOK_PATH, 'commit-msg'), 'r') as fp:
            assert install_git_hooks.COMMIT_MSG_HOOK in fp.read()

    def test_command_appends_to_existing_script(self):
        with open(os.path.join(self.command.HOOK_PATH, 'commit-msg'), 'w') as fp:
            fp.write('existing content\n')


        self.command.handle()

        with open(os.path.join(self.command.HOOK_PATH, 'commit-msg'), 'r') as fp:
            content = fp.read()

            assert content.startswith('existing content\n')
            assert 'ZERODOWNTIME_COMMIT_MSG_HOOK' in content
