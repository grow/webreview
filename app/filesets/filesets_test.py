from app import testing
from app.files import messages
import base64
import mimetypes
import md5
import unittest


class FilesetTestCase(testing.BaseTestCase):

  def setUp(self):
    super(FilesetTestCase, self).setUp()
    self.fileset = self.create_fileset()

  def _create_put_request(self, path, content):
    content_md5 = base64.b64encode(md5.new(content).digest())
    content_length = str(len(content))
    req = messages.UnsignedRequest()
    req.verb = messages.Verb.PUT
    req.path = path
    req.headers = messages.Headers()
    req.headers.content_type = mimetypes.guess_type(path)[0]
    req.headers.content_length = content_length
    req.headers.content_md5 = content_md5
    return req

  def _create_delete_request(self, path):
    req = messages.UnsignedRequest()
    req.path = path
    req.verb = messages.Verb.DELETE
    return req

  def test_create_signed_requests(self):
    reqs = [
        self._create_put_request('/foo/index.html', 'foobar'),
        self._create_put_request('/bar/index.html', 'foobaz'),
        self._create_put_request('/bam/index.html', 'foobam'),
        self._create_delete_request('/foo/index.html'),
        self._create_delete_request('/foo/index.html'),
        self._create_delete_request('/foo/index.html'),
    ]
    signed_reqs = self.fileset.sign_requests(reqs)

  def test_finalize(self):
    self.fileset.finalize()


if __name__ == '__main__':
  unittest.main()
