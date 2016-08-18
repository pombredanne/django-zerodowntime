import os
import os.path
import sys

from invoke import task


@task
def test(ctx):
    # Inspired by: https://github.com/django/django-localflavor

    print('Python version: ' + sys.version)
    test_cmd = 'coverage run `which django-admin.py` test --settings=tests.settings'
    flake_cmd = 'flake8 --ignore=W801,E128,E501,W402'

    # Fix issue #49
    cwp = os.path.dirname(os.path.abspath(__name__))
    pythonpath = os.environ.get('PYTHONPATH', '').split(os.pathsep)
    pythonpath.append(os.path.join(cwp, 'tests'))
    os.environ['PYTHONPATH'] = os.pathsep.join(pythonpath)

    # ctx.run('{0} zerodowntime'.format(flake_cmd))
    ctx.run('{0} tests'.format(test_cmd))
    # ctx.run('coverage report')
