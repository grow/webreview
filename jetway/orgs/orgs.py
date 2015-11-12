from . import memberships
from . import messages
from ..avatars import avatars
from google.appengine.ext import ndb
import os


class Error(Exception):
  pass


class OrgExistsError(Error):
  pass


class OrgConflictError(Error):
  pass


class OrgDoesNotExistError(Error):
  pass


class Org(ndb.Model):
  nickname = ndb.StringProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)
  updated = ndb.DateTimeProperty(auto_now=True)
  created_by_key = ndb.KeyProperty()
  email = ndb.StringProperty()
  location = ndb.StringProperty()
  description = ndb.StringProperty()
  website_url = ndb.StringProperty()

  def __repr__(self):
    return '<Org: {}>'.format(self.nickname)

  @classmethod
  def create(cls, nickname, created_by):
    try:
      cls.get(nickname)
      raise OrgExistsError('Org "{}" already exists.'.format(nickname))
    except OrgDoesNotExistError:
      org = cls(
          nickname=nickname,
          created_by_key=created_by.key)
      org.put()
      return org

  def delete(self):
    from jetway.projects import projects
    results = projects.Project.search(owner=self)
    if results:
      team.delete()
    self.key.delete()

  @classmethod
  def get(cls, nickname):
    query = cls.query(cls.nickname == nickname)
    results = query.fetch(1)
    result = results[0] if len(results) else None
    if result is None:
      raise OrgDoesNotExistError('Org "{}" does not exist.'.format(nickname))
    return result

  @property
  def url(self):
    scheme = os.environ['wsgi.url_scheme']
    hostname = os.environ['HTTP_HOST']
    return '{}://{}/{}'.format(scheme, hostname, self.nickname)

  @property
  def ident(self):
    return str(self.key.id())

  def update(self, message):
    try:
      if Org.get(message.nickname) != self:
        raise OrgExistsError('Nickname already in use.')
    except OrgDoesNotExistError:
      pass
    self.description = message.description
    self.location = message.location
    self.website_url = message.website_url
    self.put()

  @classmethod
  def list(cls):
    query = cls.query()
    return query.fetch()

  @property
  def avatar_url(self):
    return avatars.Avatar.create_url(self)

  def to_message(self):
    message = messages.OrgMessage()
    message.nickname = self.nickname
    message.location = self.location
    message.description = self.description
    message.created = self.created
    message.updated = self.updated
    message.avatar_url = self.avatar_url
    message.ident = self.ident
    return message
