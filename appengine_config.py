import json
import mimetypes
import os
import sys
import yaml


sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))


mimetypes.add_type('image/svg+xml', '.svg')


if os.path.exists('config/jetway.yaml'):
  jetway_config = yaml.load(open('config/jetway.yaml'))
else:
  jetway_config = yaml.load(open('config/jetway.yaml.example'))


if os.path.exists('config/client_secrets.json'):
  client_secrets_path = os.path.abspath('config/client_secrets.json')
else:
  client_secrets_path = os.path.abspath('config/client_secrets.json.example')

client_secrets = json.load(open(client_secrets_path))


if os.path.exists('config/gcs_private_key.der'):
  gcs_private_key_path = os.path.abspath('config/gcs_private_key.der')
else:
  gcs_private_key_path = os.path.abspath('config/gcs_private_key.der.example')


IS_DEV_SERVER = os.getenv('SERVER_SOFTWARE', '').startswith('Dev')


if os.environ.get('CURRENT_VERSION_ID', '') == 'testbed-version':
  PREVIEW_HOSTNAME = 'jetway-test.appspot.com'
elif IS_DEV_SERVER:
  PREVIEW_HOSTNAME = jetway_config['urls']['hostname']['dev']
else:
  PREVIEW_HOSTNAME = jetway_config['urls']['hostname']['prod']


WEBAPP2_AUTH_CONFIG = {
    'webapp2_extras.sessions': {
        'secret_key': jetway_config['app']['webapp2_secret_key'],
        'user_model': 'jetway.users.User',
    },
}


class OAuth(object):
  CLIENT_ID = client_secrets['web']['client_id']
  SCOPES = (
      'https://www.googleapis.com/auth/userinfo.email',
      'https://www.googleapis.com/auth/userinfo.profile',
  )
