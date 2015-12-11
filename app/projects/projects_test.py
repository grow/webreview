from app import testing
import unittest


class ProjectTestCase(testing.BaseTestCase):

  def setUp(self):
    super(ProjectTestCase, self).setUp()
    self.project = self.create_project()

  def test_named_filesets(self):
    named_fileset = self.project.create_named_fileset('preview', 'develop')
    ents = self.project.list_named_filesets()
    self.assertItemsEqual([named_fileset], ents)
    self.project.delete_named_fileset('preview')

  def test_transfer_owner(self):
    owner = self.project.owner
    self.assertEqual(owner, self.project.owner)
    new_owner = self.create_owner('new-owner', 'new-owner@example.com')
    self.project.transfer_owner(new_owner)
    self.assertEqual(new_owner, self.project.owner)


if __name__ == '__main__':
  unittest.main()
