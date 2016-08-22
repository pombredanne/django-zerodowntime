## django-zerodowntime with Heroku
The following conditions are assumed:

* You have a Django 1.8+ application running on Heroku
* You already use Heroku Postgres
* You already use CircleCI

### Integrating with CircleCI

1. Copy the example [PyInvoke](http://www.pyinvoke.org/) script: [tasks.py](./tasks.py)
2. Add the dependencies from [requirements.txt](./requirements.txt)
3. Modify your `circle.yml` to resemble the example below. 

#### `circle.yml`

```yaml
deployment:
  staging:
    branch: master
    commands:
      - invoke deploy:
          environment:
            HEROKU_APP_NAME: django-zdcd-poc
          timeout: 6000
```

### How this works

When your build is successful, `invoke deploy` will verify all pending migrations are safe for zero downtime deployment.  By default `invoke deploy` will only deploy releases that are safe, unsafe builds will fail and deployment will be skipped.  

The deployment process will start by capturing a backup of your Heroku Postgres database.  Once the backup is complete, pending migrations will be applied, then code will be pushed last.  The code deployment process is the usual Heroku slug build process.  The application will remain online and serving requests during this time.

When unsafe migrations are to be applied, the above process is identical except that your Heroku app will be placed in maintenance mode and all dynos scaled to zero for the duration of the deployment.  Because this will block all requests, it is recommended that you do this at night or outside of normal usage hours.  We use Heroku's scheduled tasks to execute `invoke nightly_build` to execute a build on CircleCI with `RUN_NIGHTLY_BUILD=true` as an environment variable.
