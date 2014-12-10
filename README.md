# Jetway [![Build Status](https://travis-ci.org/grow/jetway.png?branch=master)](https://travis-ci.org/grow/jetway)

The place to go to stage, preview, review, and sign off on static site builds before launch.

*NOTE*: Jetway is currently under development and is not yet ready for use.

## Contributing

## Development environment

Here's how to get started with Jetway. There are a number of manual steps needed to run a local development server due to integration with Google Accounts and Cloud Storage.

1. Jetway is an App Engine application, so create or use an existing App Engine project.
1. Acquire a *web application client secrets JSON file* from the Google Developers Console (see link below). This is used for Google OAuth authentication.
1. Also acquire a *service account JSON key* file. This is used for integration with Google Cloud Storage.
1. Place both files into the `config/` directory.
1. Copy `config/jetway.yaml.example` to `config/jetway.yaml` and follow in-file instructions.
1. Run `./scripts/setup` to install dependencies.
1. Run `./scripts/test` to verify tests pass.
1. Run `./scripts/run` to start a development server.

Google Developers Console: `https://console.developers.google.com/project/apps~<PROJECT ID>/apiui/credential`
