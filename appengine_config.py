from google.appengine.api import app_identity
import json
import mimetypes
import os
import sys
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
mimetypes.add_type('image/svg+xml', '.svg')

if 'JETWAY_CONFIG' in os.environ:
  _config_path = os.getenv('JETWAY_CONFIG')
elif os.path.exists('config/jetway.yaml'):
  _config_path = 'config/jetway.yaml'
else:
  _config_path = 'config/jetway.yaml.example'

jetway_config = yaml.load(open(_config_path))

if os.environ.get('TESTING'):
  service_account_key = json.load(open('testing/service_account_key.json'))
  client_secrets_path = os.path.abspath('testing/client_secrets.json')
elif jetway_config.get('app'):
  _basename = jetway_config['app'].get('client_secrets_file', 'client_secrets.json')
  client_secrets_path = os.path.abspath('config/{}'.format(_basename))
  client_secrets = json.load(open(client_secrets_path))
  _basename = jetway_config['app'].get('service_account_key_file', 'service_account_key.json')
  service_account_key_path = os.path.abspath('config/{}'.format(_basename))
  service_account_key = json.load(open(service_account_key_path))
else:
  client_secrets_path = os.path.abspath('testing/client_secrets.json')
  client_secrets = {'web': {'client_id': '12345', 'client_secret': '12345'}}
  service_account_key = {'client_email': None}

ALLOWED_USER_DOMAINS = jetway_config.get('options', {}).get('allowed_user_domains', None)

REQUIRE_HTTPS_FOR_PREVIEWS = jetway_config.get('require_https', {}).get('preview_domain', False)

REQUIRE_HTTPS_FOR_APP = jetway_config.get('require_https', {}).get('app_domain', False)

GCS_SERVICE_ACCOUNT_EMAIL = service_account_key['client_email']

IS_DEV_SERVER = os.getenv('SERVER_SOFTWARE', '').startswith('Dev')

if IS_DEV_SERVER:
  GCS_BUCKET = 'grow-prod.appspot.com'
else:
  GCS_BUCKET = app_identity.get_default_gcs_bucket_name()

if os.environ.get('TESTING'):
  PREVIEW_HOSTNAME = 'jetway-test.appspot.com'
elif IS_DEV_SERVER:
  PREVIEW_HOSTNAME = jetway_config['urls']['hostname']['dev']
else:
  PREVIEW_HOSTNAME = jetway_config['urls']['hostname']['prod']

BUILDBOT_API_KEY = jetway_config['app'].get('webreview_buildbot_api_key')
BUILDBOT_SERVICE_ACCOUNT = jetway_config['app'].get('webreview_buildbot_service_account')

_token_age = 60 * 60 * 24 * 7 * 4  # 4 weeks.

WEBAPP2_AUTH_CONFIG = {
    'webapp2_extras.auth': {
        'user_model': 'jetway.users.users.User',
        'token_max_age': _token_age,
        'token_new_age': _token_age,
        'token_cache_age': _token_age,
    },
    'webapp2_extras.sessions': {
        'secret_key': str(client_secrets['web']['client_secret']),
        'user_model': 'jetway.users.users.User',
    },
}

if not IS_DEV_SERVER:
  WEBAPP2_AUTH_CONFIG['webapp2_extras.sessions']['cookie_args'] = {
      'secure': True
  }

class OAuth(object):
  CLIENT_ID = client_secrets['web']['client_id']
  SCOPES = (
      'https://www.googleapis.com/auth/userinfo.email',
      'https://www.googleapis.com/auth/userinfo.profile',
  )
