# Copyright 2013 Google, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Provides a Google Cloud Storage URL signer for building requests to GCS.

Usage:

  # Creates a URL signer.
  # <path> is the absolute file path in GCS, including bucket.
  signer = CloudStorageURLSigner(...)

  # Creates or replaces a file.
  content = open(...).read()
  content_md5 = base64.b64encode(md5.new(content).digest())
  content_length = str(len(content))
  content_type = mimetypes.guess_type(...)[0]

  request = signer.put(<path>, content_type, content_length, content_md5)
  requests.put(
    request['url'],
    params=request['params'],
    headers=request['headers'],
    data=content)

  # Gets a file.
  request = signer.get(<path>)
  requests.get(
    request['url'],
    params=request['params'])

  # Deletes a file.
  request = signer.delete(<path>)
  requests.delete(
    request['url'],
    params=request['params'])
"""

import base64
import datetime
import time

import Crypto.Hash.SHA256 as SHA256
import Crypto.PublicKey.RSA as RSA
import Crypto.Signature.PKCS1_v1_5 as PKCS1_v1_5

# The Google Cloud Storage API endpoint. You should not need to change this.
GCS_API_ENDPOINT = 'https://storage.googleapis.com'


class CloudStorageURLSigner(object):
  """Contains methods for generating signed URLs for Google Cloud Storage."""

  def __init__(self, key, client_id_email, gcs_api_endpoint=GCS_API_ENDPOINT,
               expiration=None):
    """Creates a CloudStorageURLSigner that can be used to access signed URLs.

    Args:
      key: A PyCrypto private key.
      client_id_email: GCS service account email.
      gcs_api_endpoint: Base URL for GCS API.
      expiration: An instance of datetime.datetime containing the time when the
                  signed URL should expire.
    """
    self.key = RSA.importKey(key)
    self.client_id_email = client_id_email
    self.gcs_api_endpoint = gcs_api_endpoint

    self.expiration = expiration or (datetime.datetime.now() +
                                     datetime.timedelta(hours=1))
    self.expiration = int(time.mktime(self.expiration.timetuple()))

  def _Base64Sign(self, plaintext):
    """Signs and returns a base64-encoded SHA256 digest."""
    shahash = SHA256.new(plaintext)
    signer = PKCS1_v1_5.new(self.key)
    signature_bytes = signer.sign(shahash)
    return base64.b64encode(signature_bytes)

  def _MakeSignatureString(self, verb, path, content_md5, content_type):
    """Creates the signature string for signing according to GCS docs."""
    signature_string = ('{verb}\n'
                        '{content_md5}\n'
                        '{content_type}\n'
                        '{expiration}\n'
                        '{resource}')
    return signature_string.format(verb=verb,
                                   content_md5=content_md5,
                                   content_type=content_type,
                                   expiration=self.expiration,
                                   resource=path)

  def _MakeUrl(self, verb, path, content_type='', content_md5=''):
    """Forms and returns the full signed URL to access GCS."""
    base_url = '%s%s' % (self.gcs_api_endpoint, path)
    signature_string = self._MakeSignatureString(verb, path, content_md5,
                                                 content_type)
    signature_signed = self._Base64Sign(signature_string)
    query_params = {'GoogleAccessId': self.client_id_email,
                    'Expires': str(self.expiration),
                    'Signature': signature_signed}
    return base_url, query_params

  def create_get(self, path):
    """Performs a GET request.

    Args:
      path: The relative API path to access, e.g. '/bucket/object'.

    Returns:
      An instance of requests.Response containing the HTTP response.
    """
    base_url, query_params = self._MakeUrl('GET', path)
    return {
        'url': base_url,
        'params': query_params,
    }

  def create_put(self, path, content_type, content_length, content_md5):
    """Performs a PUT request.

    Args:
      path: The relative API path to access, e.g. '/bucket/object'.
      content_type: The content type to assign to the upload.
      data: The file data to upload to the new file.

    Returns:
      An instance of requests.Response containing the HTTP response.
    """
    base_url, query_params = self._MakeUrl('PUT', path, content_type,
                                           content_md5)
    headers = {}
    headers['Content-Type'] = content_type
    headers['Content-Length'] = content_length
    if content_md5:
      headers['Content-MD5'] = content_md5
    return {
        'url': base_url,
        'params': query_params,
        'headers': headers,
    }

  def create_delete(self, path):
    """Performs a DELETE request.

    Args:
      path: The relative API path to access, e.g. '/bucket/object'.

    Returns:
      An instance of requests.Response containing the HTTP response.
    """
    base_url, query_params = self._MakeUrl('DELETE', path)
    return {
        'url': base_url,
        'params': query_params,
    }
