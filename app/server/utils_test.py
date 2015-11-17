from app import testing
from app.server import utils
import unittest


class UtilsTestCase(testing.BaseTestCase):

  def test_parse_hostname(self):
    result = utils.parse_hostname('jetway-test.appspot.com')
    self.assertIsNone(None, result)

    result = utils.parse_hostname('foo--bar--baz.jetway-test.appspot.com')
    expected = ('foo', 'bar', 'baz')
    self.assertEqual(expected, result)

    result = utils.parse_hostname('bar--baz.jetway-test.appspot.com')
    expected = (None, 'bar', 'baz')
    self.assertEqual(expected, result)

    result = utils.parse_hostname('bar--baz-dot-jetway-test.appspot.com')
    expected = (None, 'bar', 'baz')
    self.assertEqual(expected, result)

    result = utils.parse_hostname('foo-dot-jetway-test.appspot.com', multitenant=False)
    expected = ('foo',)
    self.assertEqual(expected, result)

    result = utils.parse_hostname('foo-dot-jetway-test.appspot.com', multitenant=True)
    expected = None
    self.assertEqual(expected, result)

    result = utils.parse_hostname('foo--bar--baz.beta.jetway-test.appspot.com')
    expected = ('foo', 'bar', 'baz')
    self.assertEqual(expected, result)

  def test_make_url(self):
    fileset, project, owner = ('fileset', 'project', 'owner')
    expected = 'http://fileset.jetway-test.appspot.com'
    result = utils.make_url(fileset, project, owner, include_port=False)
    self.assertEqual(expected, result)
    expected = 'http://fileset.jetway-test.appspot.com:80'
    result = utils.make_url(fileset, project, owner, include_port=True)
    self.assertEqual(expected, result)

  def test_is_avatar_request(self):
    hostnames = [
        'avatars-1-dot-foo',
        'avatars-U-dot-foo',
        'avatars-a-dot-foo',
    ]
    for hostname in hostnames:
      self.assertTrue(utils.is_avatar_request(hostname))


if __name__ == '__main__':
  unittest.main()
