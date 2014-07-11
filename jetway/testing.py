from google.appengine.ext import testbed
import appengine_config
import unittest


class BaseTestCase(unittest.TestCase):

  def setUp(self):
    super(BaseTestCase, self).setUp()
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_app_identity_stub()
    self.testbed.init_blobstore_stub()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()
    self.testbed.init_urlfetch_stub()
    self.testbed.setup_env(testing='True')
    reload(appengine_config)
