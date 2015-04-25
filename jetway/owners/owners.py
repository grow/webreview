from google.appengine.ext import ndb
from jetway.avatars import avatars
from jetway.orgs import orgs
from jetway.owners import messages
from jetway.users import users
from jetway.teams import teams


class Error(Exception):
  pass


class OwnerExistsError(Error):
  pass


class OwnerDoesNotExistError(Error):
  pass


class Owner(object):

  def __init__(self, org=None, user=None):
    self.org = org
    self.user = user

  def __eq__(self, other):
    if self is None or other is None:
      return False
    return self.key == other.key

  @classmethod
  def get_by_ident(cls, ident):
    org_key = ndb.Key('Org', ident)
    user_key = ndb.Key('User', ident)
    entities = ndb.get_multi([org_key, user_key])
    for entity in entities:
      if isinstance(entity, orgs.Org):
        return cls(org=entity)
      elif isinstance(entity, users.User):
        return cls(user=entity)
    raise OwnerDoesNotExistError()

  @classmethod
  def get_by_key(cls, key):
    entity = key.get()
    if isinstance(entity, orgs.Org):
      return cls(org=entity)
    elif isinstance(entity, users.User):
      return cls(user=entity)
    raise OwnerDoesNotExistError()

  @classmethod
  def get(cls, nickname):
    try:
      return cls(org=orgs.Org.get(nickname))
    except orgs.OrgDoesNotExistError:
      pass
    try:
      return cls(user=users.User.get(nickname))
    except users.UserDoesNotExistError:
      pass
    raise OwnerDoesNotExistError('Owner "{}" not found.'.format(nickname))

  @property
  def _entity(self):
    return self.org or self.user

  @classmethod
  def search(cls):
    query = cls.query()
    return query.fetch()

  @property
  def ident(self):
    return str(self.key.id())

  @property
  def key(self):
    return self._entity.key

  @property
  def nickname(self):
    return self._entity.nickname

  @property
  def avatar_url(self):
    return avatars.Avatar.create_url(self)

  def update(self, message):
    return self._entity.update(message)

  @property
  def kind(self):
    return (messages.OwnerMessage.Kind.ORG if self.org
            else messages.OwnerMessage.Kind.USER)

  def to_message(self):
    message = messages.OwnerMessage()
    message.ident = self.ident
    message.kind = self.kind
    message.nickname = self.nickname
    message.location = self._entity.location
    message.description = self._entity.description
    message.created = self._entity.created
    message.website_url = self._entity.website_url
    message.avatar_url = self.avatar_url
    return message

  def create_team(self, nickname, created_by):
    return teams.Team.create(self, nickname, created_by)

  def search_teams(self):
    return teams.Team.search(owner=self)

  def get_team(self, nickname):
    return teams.Team.get(self, nickname)

  def delete_team(self, nickname):
    team = self.get_team(nickname)
    team.delete()
