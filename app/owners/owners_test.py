from app import testing
from app.orgs import orgs
from app.owners import owners
from app.users import users
import unittest


class OwnersTestCase(testing.BaseTestCase):

  def test_get(self):
    user = users.User.create('user')
    org = orgs.Org.create('org', created_by=user)
    owner_user = owners.Owner.get('user')
    self.assertEqual(owner_user, user)
    owner_org = owners.Owner.get('org')
    self.assertEqual(owner_org, org)


if __name__ == '__main__':
  unittest.main()
