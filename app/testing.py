from google.appengine.ext import testbed
from app.filesets import messages as fileset_messages
from app.orgs import orgs
from app.owners import owners
from app.projects import projects
from app.users import users
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

  def create_project(self):
    creator = users.User.create('creator', email='creator@example.com')
    orgs.Org.create('owner', created_by=creator)
    owner = owners.Owner.get('owner')
    return projects.Project.create(owner, 'project', created_by=creator)

  def create_fileset(self):
    project = self.create_project()
    commit = fileset_messages.CommitMessage(branch='master', sha='1234567890')
    return project.create_fileset('master', commit=commit)

  def create_owner(self, nickname, email):
    creator = users.User.create(nickname, email=email)
    return owners.Owner.get(creator.nickname)
