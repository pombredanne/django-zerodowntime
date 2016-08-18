import os
import stat

from django.core.management import BaseCommand

COMMIT_MSG_HOOK = """
# BEGIN ZERODOWNTIME_COMMIT_MSG_HOOK
commit_regex='(\[allow\-unsafe\-migrations]|merge)'

if ! grep -iqE "$commit_regex" "$1"; then
    source ./venv/bin/activate
    export $(heroku config -s | sed -e "s/='\\(.*\\)'/=\\1/")

    ./manage.py check_migrations

    migration_check=$?
    if [ $migration_check != 0 ]; then
      echo "Aborting commit, caused by migrations incompatible with ZDCD." >&2
      echo "To skip this check you can add '[skip-zdcd-check]' to your commit message." >&2
      exit $migration_check
    fi;
fi;
# END ZERODOWNTIME_COMMIT_MSG_HOOK
"""


class Command(BaseCommand):
    help = 'Installs a git commit-msg hook which will ' \
           'execute `./manage.py check_migrations` unless ' \
           'the commit message contains "[allow-unsafe-migrations]"'

    HOOK_PATH = '.git/hooks/'

    def handle(self, *args, **options):
        commit_msg_path = os.path.join(self.HOOK_PATH, 'commit-msg')

        hook_exists = os.path.exists(commit_msg_path)

        if hook_exists:
            with open(commit_msg_path, 'r') as fp:
                hook_content = fp.read()
        else:
            hook_content = '#!/usr/bin/env bash\n\n'

        if 'ZERODOWNTIME_COMMIT_MSG_HOOK' not in hook_content:
            hook_content += COMMIT_MSG_HOOK

            with open(commit_msg_path, 'w') as fp:
                fp.write(hook_content)

            st = os.stat(commit_msg_path)
            os.chmod(commit_msg_path, st.st_mode | stat.S_IEXEC)
