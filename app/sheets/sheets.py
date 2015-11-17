from googleapiclient import discovery
from oauth2client import client
#from oauth2client import keyring_storage
from oauth2client import tools
import appengine_config
import httplib2
import logging


CLIENT_ID = appengine_config.client_secrets['web']['client_id']
CLIENT_SECRET = appengine_config.client_secrets['web']['client_secret']
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'


def get_sheet(sheet_id, gid=None, ext=''):
  credentials = _get_credentials()
  http = httplib2.Http()
  http = credentials.authorize(http)
  service = discovery.build('drive', 'v2', http=http)
  resp = service.files().get(fileId=sheet_id).execute()
  for mimetype, url in resp['exportLinks'].iteritems():
    if not mimetype.endswith(ext[1:]):
      continue
    if gid:
      url += '&gid={}'.format(gid)
    resp, content = service._http.request(url)
    if resp.status != 200:
      logging.error('Error downloading Google Sheet: {}'.format(sheet_id))
      break
    return resp


def _get_credentials(self, username='default'):
  storage = keyring_storage.Storage('Jetway', username)
  credentials = storage.get()
  if credentials is None:
    parser = tools.argparser
    flags, _ = parser.parse_known_args()
    flow = client.OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE)
    credentials = tools.run_flow(flow, storage, flags)
  return credentials
