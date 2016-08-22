# django-zerodowntime

Management commands to help Django users build & deploy their projects with low interruption for their users.  This method is often called Zero Downtime Continous Delivery, or ZDCD.

Database schema migrations are the most common cause of application downtime during a deployment.  Some operations like adding a NULLed column or an entirely new table do not affect the application as it continues to run.  Other operations such as removing/renaming a column/table can cause the deployed code to fail in unexpected ways.  Ultimately you will have to remove or rename existing schema, but most deployments do not require downtime so the code can be updated without interrupting users.

This project was developed for use at [Rentlytics](http://rentlytics.com), [here is a copy](./Rentlytics-ZDCD.pdf) of the presentation which brought this project to life.

## Commands

### `check_migrations`
Checks all pending migrations against the DEFAULT Django database for zero downtime deployment compatibility.  A migration is considered compatible when it contains only: `CreateModel`, `AddField`, or `AlterModelOptions` operations.  An exception is when `AddField` is used to create a new column with a default value provided.  Providing a default value requires filling all existing rows with the value, which can be an expensive operation.


### `insert_git_hooks`
Adds or modifies the git `commit-msg` hook at `.git/hooks/commit-msg` to execute `check_migrations` before each commit is saved to git's history.  When `check_migrations` exits with a non-zero exit code, an error message will be output listing the incompatible migration operations.  In the event that incompatible migrations are to be allowed, you can add `[allow-unsafe-migrations]` to your commit message, which skips this check.


## Usage Guide
The following conditions are assumed:

* You have a Django 1.8+ application running on Heroku
* You already use Heroku Postgres
* You already use Continuous Integration, such as: CircleCI, Jenkins, or TravisCI

### Integrating with existing Continuous Integration

1. Copy our example [PyInvoke](http://www.pyinvoke.org/) script: [tasks.py](./examples/heroku/tasks.py) 
3. In your CI system:
    1. Add an environment variable named `HEROKU_APP_NAME`, set it to the target Heroku app name.
    2. Execute `invoke deploy` to the deployment steps.

When your build is successful, `invoke deploy` will check the pending migrations against your Heroku database for ZDCD compatability.  If the migrations are incompatible, the script will exit and your existing application will be unmodified.  If the migrations are compatible, then a database backup will be captured.  After the database is backed up, your code will be pushed via git to Heroku, and the normal deploy process will take over.  If for any reason there is a failure in the deployment process, then your app and database will be rolled back to the previous released version.

Deploys containing migrations which are considered unsafe should be performed outside of normal usage.  We use Heroku's scheduled tasks to execute `invoke nightly_build` to execute a build on CircleCI.  Nightly builds are allowed to run all migrations by passing `NIGHTLY_BUILD=true` as an environment variable.

#### CircleCI `circle.yml` example
```yaml
dependencies:
  override:
    - pip install invoke

deployment:
  staging:
    branch: master
    commands:
      - invoke deploy:
          environment:
            HEROKU_APP_NAME: django-zdcd-poc
          timeout: 6000
```
