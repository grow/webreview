from . import memberships
from . import messages
from ..avatars import avatars
from ..teams import teams
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
      teams.Team.create(org, None, created_by=created_by,
                        kind=teams.messages.Kind.ORG_OWNERS)
      return org

  def delete(self):
    from jetway.projects import projects
    results = projects.Project.search(owner=self)
    if results:
      raise OrgConflictError('Cannot delete organizations that have projects.')
    results = teams.Team.search(owner=self)
    for team in results:
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

  def search_members(self):
    team_objs = teams.Team.search(owner=self)
    user_keys = []
    for team in team_objs:
      user_keys += team.user_keys
    return ndb.get_multi(list(set(user_keys)))

  def get_team_membership(self, user):
    team_objs = self.list_teams()
    team_keys = [team.key for team in team_objs]
    query = teams.TeamMembership.query()
    query = query.filter(teams.TeamMembership.parent_key.IN(team_keys))
    query = query.filter(teams.TeamMembership.user_key == user.key)
    results = query.fetch(1)
    result = results[0] if len(results) else None
    if result is None:
      text = '{} is not a member of any team in {}.'
      raise memberships.MembershipDoesNotExistError(text.format(user, self))
    return result

  def create_team_membership(self, team, user, role):
    # multipel teams, so parent isnt always the same
    try:
      self.get_team_membership(user)
      text = '{} is already a member of a team in {}.'
      raise memberships.MembershipExistsError(text.format(user, self))
    except memberships.MembershipDoesNotExistError:
      return team.create_membership(user, role)

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
