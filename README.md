# Getting started with Django on Pivotal Cloud Foundry

This is an app for managing Pivotal standup hosts. 
It can be used as an example of how to run a [Django](https://www.djangoproject.com/) 
app on Pivotal Cloud Foundry.

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