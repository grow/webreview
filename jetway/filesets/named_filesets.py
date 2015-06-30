from google.appengine.ext import ndb
from . import filesets
from . import messages

class Error(Exception):
  pass


class NamedFilesetExistsError(Error):
  pass


class NamedFileset(ndb.Model):
  name = ndb.StringProperty()
  branch = ndb.StringProperty()
  project_key = ndb.KeyProperty()

  @classmethod
  def create(cls, project, branch, name):
    named_fileset = cls.get(name)
    if named_fileset is None:
      named_fileset = cls(id=name)
      named_fileset.project_key = project.key
      named_fileset.branch = branch
      named_fileset.put()
    return named_fileset

  @classmethod
  def get(cls, name):
    return cls.get_by_id(name)

  @property
  def ident(self):
    return str(self.key.id())

  @classmethod
  def search(cls, project):
    query = cls.query()
    query = query.filter(cls.project_key == project.key)
    return query.fetch()

  def get_fileset(self):
    return filesets.Fileset.get(branch=branch)

  def delete(self):
    self.key.delete()

  def to_message(self):
    message = messages.NamedFilesetMessage()
    message.branch = self.branch
    message.project = self.project.to_message()
    return message
