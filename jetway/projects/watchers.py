from google.appengine.ext import ndb
from . import watcher_messages as messages


class Watcher(ndb.Model):
  created = ndb.DateTimeProperty(auto_now_add=True)
  project_key = ndb.KeyProperty()
  user_key = ndb.KeyProperty()

  @property
  def ident(self):
    return str(self.key.id())

  @classmethod
  def create(cls, project, user):
    watcher = cls.get(project, user)
    if watcher:
      return watcher
    watcher = cls(project_key=project.key, user_key=user.key)
    watcher.put()
    return watcher

  @classmethod
  def get(cls, project, user):
    query = cls.query()
    query.filter(cls.project_key == project.key)
    query.filter(cls.user_key == user.key)
    return query.get()

  def delete(self):
    self.key.delete()

  @property
  def user(self):
    return self.user_key.get()

  @property
  def project(self):
    return self.project_key.get()

  @classmethod
  def search(cls, project):
    query = cls.query()
    query = query.filter(cls.project_key == project.key)
    return query.fetch()

  def to_message(self):
    message = messages.WatcherMessage()
    message.project = self.project.to_message()
    message.user = self.user.to_message()
    message.ident = self.ident
    return message
