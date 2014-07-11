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
        open(appengine_config.gcs_private_key_path).read(),
        appengine_config.jetway_config['app']['gcs_service_account_email'])

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
    req.params = messages.Params()
    req.params.google_access_id = request['params']['GoogleAccessId']
    req.params.expires = request['params']['Expires']
    req.params.signature = request['params']['Signature']
    req.headers = messages.Headers()
    req.headers.content_type = request['headers']['Content-Type']
    req.headers.content_length = request['headers']['Content-Length']
    if 'Content-MD5' in request['headers']:
      req.headers.content_md5 = request['headers']['Content-MD5']
    return req

  def sign_delete_request(self, unsigned_request):
    absolute_path = os.path.join(self.root, unsigned_request.path.lstrip('/'))
    request = self.signer.create_delete(absolute_path)
    req = messages.SignedRequest()
    req.path = unsigned_request.path
    req.verb = messages.Verb.DELETE
    req.url = request['url']
    req.params = messages.Params()
    req.params.google_access_id = request['params']['GoogleAccessId']
    req.params.expires = request['params']['Expires']
    req.params.signature = request['params']['Signature']
    return req

  def get_headers_for_path(self, path, request_headers=None):
    absolute_path = os.path.join(self.root, path.lstrip('/'))
    try:
      stat = cloudstorage.stat(absolute_path)
    except cloudstorage.errors.NotFoundError as e:
      raise FileNotFoundError(str(e))

    headers = {}
    time_obj = datetime.fromtimestamp(stat.st_ctime).timetuple()
    headers['Last-Modified'] =  time.strftime('%a, %d %b %Y %H:%M:%S GMT', time_obj)
    headers['ETag'] = '"{}"'.format(stat.etag)
    headers['X-Jetway-Storage-Key'] = str(absolute_path)
    if stat.content_type:
      headers['Content-Type'] = stat.content_type

    # Only add X-AppEngine-BlobKey if needed, based on ETag.
    request_headers = request_headers or {}
    request_etag = request_headers.get('If-None-Match')
    if request_etag != headers['ETag']:
      key = blobstore.create_gs_key('/gs{}'.format(absolute_path))
      headers['X-AppEngine-BlobKey'] = key

    return headers

  def delete(self, path, silent=False):
    try:
      absolute_path = os.path.join(self.root, path.lstrip('/'))
      cloudstorage.delete(absolute_path)
    except cloudstorage.errors.NotFoundError:
      if not silent:
        raise
