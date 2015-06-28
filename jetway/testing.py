from google.appengine.ext import testbed
from jetway.filesets import messages as fileset_messages
from jetway.orgs import orgs
from jetway.owners import owners
from jetway.projects import projects
from jetway.users import users
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
    self.testbed.init_user_stub()
    self.testbed.init_mail_stub()
    self.testbed.setup_env(testing='True')
    reload(appengine_config)

  def create_fileset(self):
    creator = users.User.create('creator', email='creator@example.com')
    org = orgs.Org.create('owner', created_by=creator)
    owner = owners.Owner.get('owner')
    project = projects.Project.create(owner, 'project', created_by=creator)
    commit = fileset_messages.CommitMessage(branch='master', sha='1234567890')
    return project.create_fileset('master', commit=commit)
