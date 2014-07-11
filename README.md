# Jetway [![Build Status](https://travis-ci.org/grow/jetway.png?branch=master)](https://travis-ci.org/grow/jetway)

The place to go to stage, preview, review, and sign off on static site builds before launch.

## Contributing

### Config files

#### Generating gcs_private_key.der

Jetway requires a config file `gcs_private_key.der` in the config directory. You can generate this file from your project in the Google Cloud Developer Console.

1. Visit https://console.developers.google.com/project/apps~<PROJECT ID>/apiui/credential
1. Click "create new client id" and choose "service account".
1. Click "generate new P12 key".

Run the following commands with the downloaded `<key>.p12` file in the config folder:

    openssl pkcs12 -in *.p12 -nodes -nocerts > key.pem
    openssl rsa -in key.pem -inform PEM -out gcs_private_key.der -outform DER##
