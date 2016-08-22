import contextlib
import json
import logging
import os
import re
import requests

from invoke import task

logger = logging.getLogger(__name__)


def header(message):
    print('-----> ' + message)


@task
def heroku_app_name(ctx=None):
    name = os.environ.get('HEROKU_APP_NAME')
    if not isinstance(name, str) or len(name) == 0:
        raise EnvironmentError("Please set environment variable `HEROKU_APP_NAME` to the Heroku app name.")

    return name


@task(pre=[heroku_app_name])
def heroku_setup_cli(ctx):
    ctx.run('git remote add heroku git@heroku.com:{}.git'.format(heroku_app_name(ctx)))

    output = ctx.run('heroku config -s', hide='stdout')

    for line in output.stdout.splitlines():
        key, value = line.split('=', 1)

        os.environ[key] = value.strip("'")


def heroku_current_version(ctx):
    result = ctx.run('heroku releases --json -n 1', hide='stdout')
    versions = json.loads(result.stdout)

    return versions[0]['version']


@contextlib.contextmanager
def heroku_maintenance_mode(ctx):
    ctx.run('heroku maintenance:on')
    result = ctx.run('heroku ps:scale')

    dyno_formation = result.stdout

    zeroed_dynos = re.sub(r'\d+', '0', dyno_formation)
    ctx.run('heroku ps:scale {}'.format(zeroed_dynos))

    yield

    ctx.run('heroku ps:scale {}'.format(dyno_formation))
    ctx.run('heroku maintenance:off')


@contextlib.contextmanager
def rollback_on_failure(ctx, released_version, database_backup):
    try:
        yield
    except Exception as exc:
        msg = 'Error during deploy, rolling back ' \
              'application to v{} & database to {} .'.format(
            released_version,
            database_backup
        )

        logger.exception(msg, exc_info=exc)

        with heroku_maintenance_mode(ctx):
            ctx.run('heroku pg:backups restore --wait-interval 60 --confirm {}'.format(heroku_app_name()))

            if released_version != heroku_current_version(ctx):
                ctx.run('heroku releases:rollback {}'.format(released_version))


def heroku_database_backup(ctx):
    result = ctx.run('heroku pg:backups capture --wait-interval 60')

    backup_id = None

    for line in result.stdout.splitlines():
        if '---backup--->' in line:
            backup_id = line[line.index('--->') + 4:].strip()
            break

    if backup_id is None:
        raise ValueError("Could not parse database backup ID from:\n\n{}".format(result.stdout))

    return backup_id


def is_nightly_build():
    return os.environ.get('RUN_NIGHTLY_BUILD') == 'true'


@task(pre=[heroku_setup_cli])
def check_migration_status(ctx):
    if is_nightly_build():
        header("Skipping migration check for nightly build.")
    else:
        header('Checking pending migrations for ZDCD compatability.')
        ctx.run('./manage.py check_migrations')
        print('PASS!')


def do_deployment(ctx, released_version, database_backup):
    header('Before deployment released_version[{}], database_backup[{}].'.format(
        released_version,
        database_backup
    ))

    with rollback_on_failure(ctx, released_version, database_backup):
        header('Migrating database')
        ctx.run('./manage.py migrate')

        header('Deploying code')
        ctx.run('git push heroku HEAD:refs/heads/master')


@task
def compare_git_hashes(ctx):
    header('Checking local git-HEAD against heroku git-HEAD')

    ctx.run('git remote update heroku', hide='stdout')

    git_revs = ctx.run('git diff --quiet HEAD heroku/master', hide='stdout', warn=True)

    if git_revs.exited == 0:
        print('local matches heroku, nothing to deploy.')
        exit(0)
    else:
        print('local does not match heroku, continuing with deploy.')


@task(pre=[heroku_setup_cli, compare_git_hashes, check_migration_status])
def deploy(ctx):
    header('Backing up database')
    released_version = heroku_current_version(ctx)
    database_backup = heroku_database_backup(ctx)

    if is_nightly_build():
        with heroku_maintenance_mode(ctx):
            do_deployment(ctx, released_version, database_backup)
    else:
        do_deployment(ctx, released_version, database_backup)

@task
def nightly_build(ctx, project_name, branch_name, circle_token):
    url = 'https://circleci.com/api/v1/project/{}/tree/{}?circle-token={}'.format(
        project_name,
        branch_name,
        circle_token
    )

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

    body = {
        'build_parameters': {
            'RUN_NIGHTLY_BUILD': "true",
        }
    }

    response = requests.post(url, json=body, headers=headers)

    print("Nightly Build queued on CircleCI: http_status={}, response={}".format(
        response.status_code,
        response.json()
    ))
