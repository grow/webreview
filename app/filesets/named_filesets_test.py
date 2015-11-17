from app import testing
from . import named_filesets
import unittest


class NamedFilesetTestCase(testing.BaseTestCase):

  def setUp(self):
    super(NamedFilesetTestCase, self).setUp()
    self.project = self.create_project()

  def test_get(self):
    named_fileset = self.project.create_named_fileset('preview', 'develop')
    ent = named_filesets.NamedFileset.get('preview')
    self.assertEqual(named_fileset, ent)
    ent.to_message()


if __name__ == '__main__':
  unittest.main()
