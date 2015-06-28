from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from jetway.files import files
from jetway.files import messages as file_messages
import appengine_config
import datetime
import time
import os
import webapp2
import pydenticon


class Error(Exception):
  pass


class AvatarDoesNotExistError(Error):
  pass


class Avatar(ndb.Model):
  gs_basename = ndb.StringProperty()

  @property
  def ident(self):
    return self.key.string_id()

  @classmethod
  def get(cls, letter, ident):
    ident = '{}/{}'.format(letter, ident)
    avatar = ndb.Key('Avatar', ident).get()
    if avatar is None:
      raise AvatarDoesNotExistError('Avatar does not exist.')
    return avatar

  @classmethod
  def create(cls, letter, ident, gs_object_name):
    gs_basename = os.path.basename(gs_object_name)
    ident = '{}/{}'.format(letter, ident)
    key = ndb.Key('Avatar', ident)
    avatar = cls(key=key, gs_basename=gs_basename)
    avatar.put()
    return avatar

  @webapp2.cached_property
  def _signer(self):
    gcs_bucket = appengine_config.get_gcs_bucket()
    root = '/{}/jetway/avatars/{}'.format(gcs_bucket, self.ident)
    return files.Signer(root)

  def sign_put_request(self, headers):
    unsigned_request = file_messages.UnsignedRequest()
    unsigned_request.headers = headers
    unsigned_request.verb = file_messages.Verb.PUT
    unsigned_request.path = 'avatar'
    return self._signer.sign_put_request(unsigned_request)

  def get_headers(self, request_headers=None):
    return self._signer.get_headers_for_path(
        self.gs_basename, request_headers=request_headers)

  @classmethod
  def create_upload_url(cls, entity):
    gcs_bucket = appengine_config.get_gcs_bucket()
    letter = entity.key.kind()[:1].lower()
    avatar_ident = '{}/{}'.format(letter, entity.ident)
    root = '{}/jetway/avatars/{}'.format(gcs_bucket, avatar_ident)
    return blobstore.create_upload_url('/avatars/{}'.format(avatar_ident), gs_bucket_name=root)

  def update(self, gs_object_name):
    if self.gs_basename:
      self._signer.delete(self.gs_basename, silent=True)
    self.gs_basename = os.path.basename(gs_object_name)
    self.put()

  @classmethod
  def create_url(cls, owner):
    path = '/avatars/{}/{}'.format(owner.key.kind()[:1].lower(), owner.ident)
    if os.getenv('SERVER_SOFTWARE', '').startswith('Dev'):
      return path
    num = owner.ident[0]
    scheme = os.getenv('wsgi.url_scheme')
    hostname = os.getenv('DEFAULT_VERSION_HOSTNAME')
    sep = '.' if scheme == 'http' else '-dot-'
    return '//avatars{}{}{}{}'.format(num, sep, hostname, path)

  @classmethod
  def generate(cls, ident):
    foreground = [
        '#F44336',
        '#E91E63',
        '#9C27B0',
        '#673AB7',
        '#3F51B5',
        '#2196F3',
        '#03A9F4',
        '#00BCD4',
        '#009688',
        '#4CAF50',
        '#8BC34A',
        '#FF9800',
        '#FF5722',
    ]
    generator = pydenticon.Generator(5, 5, foreground=foreground)
    content = generator.generate(ident, 240, 240)
    time_obj = (datetime.datetime.now() - datetime.timedelta(days=1)).timetuple()
    resp_headers = {}
    resp_headers['Content-Type'] = 'image/png'
    resp_headers['ETag'] = '"{}"'.format(ident)
    resp_headers['Last-Modified'] =  time.strftime('%a, %d %b %Y %H:%M:%S GMT', time_obj)
    return resp_headers, content
