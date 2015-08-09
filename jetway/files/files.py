import appengine_config
import cloudstorage
from datetime import datetime
from google.appengine.ext import blobstore
from jetway.files import messages
from jetway.utils import gcs
import os
import time


class Error(Exception):
  pass


class FileNotFoundError(Error):
  pass


class Signer(object):

  def __init__(self, root):
    self.root = root
    self.signer = gcs.CloudStorageURLSigner(
        appengine_config.service_account_key['private_key'],
        appengine_config.GCS_SERVICE_ACCOUNT_EMAIL)

  def sign_put_request(self, unsigned_request):
    absolute_path = os.path.join(self.root, unsigned_request.path.lstrip('/'))
    request = self.signer.create_put(
        absolute_path,
        unsigned_request.headers.content_type,
        unsigned_request.headers.content_length,
        unsigned_request.headers.content_md5)
    req = messages.SignedRequest()
    req.path = unsigned_request.path
    req.verb = messages.Verb.PUT
    req.url = request['url']
    req.params = self._create_params_message_from_request(request)
    req.headers = messages.Headers()
    req.headers.content_type = request['headers']['Content-Type']
    req.headers.content_length = request['headers']['Content-Length']
    if 'Content-MD5' in request['headers']:
      req.headers.content_md5 = request['headers']['Content-MD5']
    return req

  def sign_get_request(self, unsigned_request):
    absolute_path = os.path.join(self.root, unsigned_request.path.lstrip('/'))
    request = self.signer.create_get(absolute_path)
    req = messages.SignedRequest()
    req.path = unsigned_request.path
    req.verb = messages.Verb.GET
    req.url = request['url']
    req.params = self._create_params_message_from_request(request)
    return req

  def sign_delete_request(self, unsigned_request):
    absolute_path = os.path.join(self.root, unsigned_request.path.lstrip('/'))
    request = self.signer.create_delete(absolute_path)
    req = messages.SignedRequest()
    req.path = unsigned_request.path
    req.verb = messages.Verb.DELETE
    req.url = request['url']
    req.params = self._create_params_message_from_request(request)
    return req

  def _create_params_message_from_request(self, request):
    params = messages.Params()
    params.google_access_id = request['params']['GoogleAccessId']
    params.expires = request['params']['Expires']
    params.signature = request['params']['Signature']
    return params

  def get_headers_for_path(self, path, request_headers=None):
    absolute_path = os.path.join(self.root, path.lstrip('/'))
    try:
      stat = cloudstorage.stat(absolute_path)
    except cloudstorage.errors.NotFoundError as e:
      raise FileNotFoundError(str(e))
    headers = {}
    time_obj = datetime.fromtimestamp(stat.st_ctime).timetuple()
    time_format = '%a, %d %b %Y %H:%M:%S GMT'
    headers['Last-Modified'] = time.strftime(time_format, time_obj)
    headers['ETag'] = '"{}"'.format(stat.etag)
    headers['X-WebReview-Storage-Key'] = str(absolute_path)
    if stat.content_type:
      headers['Content-Type'] = stat.content_type
    # Only add X-AppEngine-BlobKey if needed, based on ETag.
    request_headers = request_headers or {}
    request_etag = request_headers.get('If-None-Match')
    if request_etag != headers['ETag']:
      key = blobstore.create_gs_key('/gs{}'.format(absolute_path))
      headers['X-AppEngine-BlobKey'] = key
      if os.getenv('HTTP_RANGE'):
        headers['X-AppEngine-BlobRange'] = os.getenv('HTTP_RANGE')
    return headers

  def delete(self, path, silent=False):
    try:
      absolute_path = os.path.join(self.root, path.lstrip('/'))
      cloudstorage.delete(absolute_path)
    except cloudstorage.errors.NotFoundError:
      if not silent:
        raise
