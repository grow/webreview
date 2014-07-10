from google.appengine.ext import testbed
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
    self.testbed.setup_env(
        gcs_bucket='grow-prod-grow',
        gcs_service_account_email=(
              '578372381550-gg1pnu229oppq27dc8mdihq51qbu6aq9'
              '@developer.gserviceaccount.com'),
    )
