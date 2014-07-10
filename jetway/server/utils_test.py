from jetway import testing
from jetway.server import utils
import os
import unittest


class UtilsTestCase(testing.BaseTestCase):

  def test_parse_hostname(self):
    os.environ['DEFAULT_VERSION_HOSTNAME'] = 'grow.fm'

    result = utils.parse_hostname('grow.fm')
    self.assertIsNone(None, result)

    result = utils.parse_hostname('foo--bar--baz.grow.fm')
    expected = ('foo', 'bar', 'baz')
    self.assertEqual(expected, result)

    os.environ['DEFAULT_VERSION_HOSTNAME'] = 'beta.grow.fm'
    result = utils.parse_hostname('foo--bar--baz.beta.grow.fm')
    self.assertEqual(expected, result)

    result = utils.parse_hostname('bar--baz.grow.fm')
    expected = (None, 'bar', 'baz')
    self.assertEqual(expected, result)


if __name__ == '__main__':
  unittest.main()
