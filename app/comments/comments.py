from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop
from app.comments import messages
from app.launches import launches


class Error(Exception):
  pass


class CommentDoesNotExistError(Error):
  pass


class Comment(ndb.Model):
  created = ndb.DateTimeProperty(auto_now_add=True)
  modified = ndb.DateTimeProperty(auto_now=True)
  created_by_key = ndb.KeyProperty()
  content = ndb.StringProperty()
  parent_key = ndb.KeyProperty()
  kind = msgprop.EnumProperty(messages.Kind)

  @property
  def created_by(self):
    return self.created_by_key.get()

  @property
  def ident(self):
    return str(self.key.id())

  @classmethod
  def create(cls, parent, created_by, content, kind):
    comment = cls()
    comment.parent_key = parent.key
    comment.created_by_key = created_by.key
    comment.content = content
    comment.kind = kind
    comment.put()
    return comment

  @classmethod
  def get(cls, ident):
    key = ndb.Key('Comment', int(ident))
    comment = key.get()
    if comment is None:
      raise CommentDoesNotExistError('Comment {} does not exist.'.format(ident))
    return comment

  @classmethod
  def _query(cls, parent, kind):
    query = cls.query()
    query = query.order(cls.created)
    query = query.filter(cls.kind == kind)
    query = query.filter(cls.parent_key == parent.key)
    return query

  @classmethod
  def search(cls, parent, kind):
    query = cls._query(parent, kind)
    return query.fetch()

  @classmethod
  def count(cls, parent, kind):
    query = cls._query(parent, kind)
    return query.count()

  def delete(self):
    return self.key.delete()

  def to_message(self):
    message = messages.CommentMessage()
    message.ident = self.ident
    message.created = self.created
    message.created_by = self.created_by.to_message()
    message.modified = self.modified
    message.content = self.content
    return message

  @classmethod
  def get_parent(cls, message):
    if message.kind == messages.Kind.LAUNCH:
      return launches.Launch.get_by_ident(message.parent.ident)
    raise ValueError('Invalid kind.')
