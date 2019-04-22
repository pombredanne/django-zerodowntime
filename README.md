# django-zerodowntime

[![CircleCI](https://circleci.com/gh/rentlytics/django-zerodowntime.svg?style=svg)](https://circleci.com/gh/rentlytics/django-zerodowntime)

Management commands to help Django users build & deploy their projects with low interruption for their users.  This method is often called Zero Downtime Continous Delivery, or ZDCD.

Database schema migrations are the most common cause of application downtime during a deployment.  Some operations like adding a NULLed column or an entirely new table do not affect the application as it continues to run.  Other operations such as removing/renaming a column/table can cause the deployed code to fail in unexpected ways.  Ultimately you will have to remove or rename existing schema, but most deployments do not require downtime so the code can be updated without interrupting users.

This project was developed for use at [Rentlytics](http://rentlytics.com), [here is a copy](./Rentlytics-ZDCD.pdf) of the presentation which brought this project to life.

## Commands

### `check_migrations`
Checks all pending migrations against the DEFAULT Django database for zero downtime deployment compatibility.  A migration is considered compatible when it contains only: `CreateModel`, `AddField`, or `AlterModelOptions` operations.  An exception is when `AddField` is used to create a new column with a default value provided.  Providing a default value requires filling all existing rows with the value, which can be an expensive operation.


### `insert_git_hooks` [deprecated]
Adds or modifies the git `commit-msg` hook at `.git/hooks/commit-msg` to execute `check_migrations` before each commit is saved to git's history.  When `check_migrations` exits with a non-zero exit code, an error message will be output listing the incompatible migration operations.  In the event that incompatible migrations are to be allowed, you can add `[allow-unsafe-migrations]` to your commit message, which skips this check.


## Usage Guide
* [Heroku + CircleCI](./examples/heroku/)

## Running tests
1. Ensure `tox` is installed with `pip install tox`
2. Use `tox` to run tests against py2.7 and py3.5.
    3. _You can also run `py.test` in the project root to run against   your environment's python._


### Tests Structure
The tests folder contains a Django project with 3 apps:

* conflicting_migrations
* safe_migrations
* unsafe_migrations

These apps provide test coverage for different scenarios of migrations to test, they only contain the minimum required files (`models.py` and a `migrations` folder) to act as a Django app.  Tests use different combinations of these apps to simulate realistic migration scenarios for testing.

### Making a release
For Rentlytics employees, to release new code for the django-zerodowntime project to pypi, follow these steps:

1. Setup pypi authentication for the `rentlytics` user, see [this link](http://peterdowns.com/posts/first-time-with-pypi.html)
2. Run `bumpversion` to bump the version
3. run `make release` to push the new code to PyPi

