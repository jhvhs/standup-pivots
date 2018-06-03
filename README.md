# Getting started with Django on Pivotal Cloud Foundry

This is an app for managing Pivotal standup hosts. The main assumption is
that the hosts are rotating on a weekly basis.

This app can be used as an example of how to run a [Django](https://www.djangoproject.com/) 
app on Pivotal Cloud Foundry.

# Deploying for the first time

1. The app is configured to use a postgres database by default. When using a
different database, change the `requirements.txt` to include the necessary drivers.
Aside from that, binding the database service instance to the app should work
out of the box.

1. It is necessary to set the `APP_SECRET_KEY` environment variable to a random hex string.

1. When deploying the app for the first time, the database migrations should be applied.
See https://banck.net/2014/12/deploying-a-django-application-to-cloud-foundry/ for an example of
running a database migration, followed by creating an admin user for the admin UI.

1. Once the app is up and running, go to the admin UI located at `<your-app-url>/admin`, and
use the credentials from the previous step. First, fill in the pivots. The most tricky bit is the
slack handle a.k.a Slack member ID. It can either be located by viewing the person's profile in
slack and clicking a button with a V-shaped down arrow, or retrieved via the 
[users.lookupByEmail](https://api.slack.com/methods/users.lookupByEmail) or
[users.list](https://api.slack.com/methods/users.list) API methods.

1. _(Optional)_ If you want to manually set the standup schedules, fill them as well in the admin UI.
Otherwise, they will be automatically set when accessing the public endpoints.

# Public endpoints

The app has two public endpoints:

- `/` displays a human-readable schedule with the standup pair for the current and the next week.
- `/slack_notification/` provides a short message that can be posted using an [incoming web-hook
integration](https://api.slack.com/incoming-webhooks) for Slack, e.g. a concourse resource (see below). 

# Notifying the hosts

It's easy to make slack notifications a few days ahead of the week with a concourse pipeline.
For an example, take a look at `notification-pipeline.yml`. In order to use the pipeline,
you will need a slack incoming webhook integration for the channel, and a URL to the root of the
deployed application. With these, you can set a concourse pipeline:

```bash
$ fly -t wings set-pipeline -p standup-notification -c notification-pipeline.yml \
  -v slack-notification-url=https://hooks.slack.com/services/FOO/BAR/baz \
  -v standup-app-url=https://my-standup.cf-app.com
```

By default, the pipeline triggers once every Thursday afternoon, but that can be easily
changed by editing the `notification-pipeline.yml`.