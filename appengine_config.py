import json
import mimetypes
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

mimetypes.add_type('image/svg+xml', '.svg')

if os.path.exists('client_secrets.json'):
  client_secrets_path = os.path.abspath('client_secrets.json')
else:
  client_secrets_path = os.path.abspath('client_secrets.json.example')

client_secrets = json.load(open(client_secrets_path))

IS_DEV_SERVER = os.getenv('SERVER_SOFTWARE', '').startswith('Dev')

PREVIEW_HOSTNAME = 'jetway.dev' if IS_DEV_SERVER else 'jetway.appspot.com'

WEBAPP2_AUTH_CONFIG = {
    'webapp2_extras.sessions': {
        'secret_key': '5uxIj7*3V7CxTi~=Ap{@+"*ep{1B6O',
        'user_model': 'jetway.users.User',
    },
}

class OAuth(object):
  CLIENT_ID = client_secrets['web']['client_id']
  SCOPES = (
      'https://www.googleapis.com/auth/userinfo.email',
      'https://www.googleapis.com/auth/userinfo.profile',
  )
