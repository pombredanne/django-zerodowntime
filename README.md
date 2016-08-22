# django-zerodowntime

[![CircleCI](https://circleci.com/gh/rentlytics/django-zerodowntime.svg?style=svg)](https://circleci.com/gh/rentlytics/django-zerodowntime)

Management commands to help Django users build & deploy their projects with low interruption for their users.  This method is often called Zero Downtime Continous Delivery, or ZDCD.

Database schema migrations are the most common cause of application downtime during a deployment.  Some operations like adding a NULLed column or an entirely new table do not affect the application as it continues to run.  Other operations such as removing/renaming a column/table can cause the deployed code to fail in unexpected ways.  Ultimately you will have to remove or rename existing schema, but most deployments do not require downtime so the code can be updated without interrupting users.

This project was developed for use at [Rentlytics](http://rentlytics.com), [here is a copy](./Rentlytics-ZDCD.pdf) of the presentation which brought this project to life.

## Commands

### `check_migrations`
Checks all pending migrations against the DEFAULT Django database for zero downtime deployment compatibility.  A migration is considered compatible when it contains only: `CreateModel`, `AddField`, or `AlterModelOptions` operations.  An exception is when `AddField` is used to create a new column with a default value provided.  Providing a default value requires filling all existing rows with the value, which can be an expensive operation.


### `insert_git_hooks`
Adds or modifies the git `commit-msg` hook at `.git/hooks/commit-msg` to execute `check_migrations` before each commit is saved to git's history.  When `check_migrations` exits with a non-zero exit code, an error message will be output listing the incompatible migration operations.  In the event that incompatible migrations are to be allowed, you can add `[allow-unsafe-migrations]` to your commit message, which skips this check.


## Usage Guide
* [Heroku + CircleCI](./examples/heroku/)
