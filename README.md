# WebReview [![Build Status](https://travis-ci.org/grow/webreview.png?branch=master)](https://travis-ci.org/grow/webreview)

The place to go to stage, preview, review, and sign off on static site builds before launch.

*NOTE*: WebReview is currently under development and is not yet ready for use.

## How it works

WebReview is a web workflow management app. Users create projects, add team members, and link Git repositories to those projects. WebReview provides a place for the whole team to preview website builds, manage issues and leave comments, and edit, review, and approve structured content and translations.

When a Git repository is linked to a project in WebReview, WebReview kicks off a worker that rebuilds and tests the site at the most recent commit. The build is deployed as a static fileset to Google Cloud Storage, which WebReview proxies to serve site previews.

## Contributing

### Development environment

#### Get started

Here's how to get started with WebReview. There are a number of manual steps needed to run a local development server due to integration with Google Accounts and Cloud Storage.

Run the below command and follow the on-screen instructions to install dependencies and acquire keys for integration with Google OAuth and Google Cloud Storage.

    ./scripts/setup

1. Run `./scripts/test` to verify tests pass.
1. Run `./scripts/run` to start a development server.

WebReview uses Bower to manage frontend dependencies, and Gulp to watch for changes and recompile files.

#### Development server hostnames

In production, the workflow frontend and site previews run on different domains. To mimic this behavior in development, we recommend using a modified `/etc/hosts` file. Since Google OAuth doesn't permit `.dev` URLs, we use `dev.example.com`.

```
127.0.0.1       webrev.dev.example.com
127.0.0.1       fuyu-dot-webrev.dev.example.com
127.0.0.1       itsy-dot-webrev.dev.example.com
```

Using the above configuration, requests to `webrev.dev.example.com` would serve the workflow frontend. Requests to the latter two domains would serve previews for builds named `fuyu` and `itsy`, respectively.
