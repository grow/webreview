from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop
import uuid
from jetway.teams import messages


class Error(Exception):
  pass


class TeamExistsError(Error):
  pass


class TeamDoesNotExistError(Error):
  pass


class MembershipConflictError(Error):
  pass


class ProjectConflictError(Error):
  pass


class CannotDeleteMembershipError(Error):
  pass


class TeamMembership(ndb.Model):
  role = msgprop.EnumProperty(messages.Role, default=messages.Role.READ_ONLY)
  is_public = ndb.BooleanProperty(default=False)
  domain_key = ndb.KeyProperty()
  user_key = ndb.KeyProperty()

  @property
  def domain(self):
    return self.domain_key.get()

  @property
  def user(self):
    return self.user_key.get()

  def to_message(self):
    message = messages.TeamMembershipMessage()
    message.user = self.user.to_message()
    message.is_public = self.is_public
    message.role = self.role
    return message


class Team(ndb.Model):
  owner_key = ndb.KeyProperty()
  nickname = ndb.StringProperty()
  description = ndb.StringProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)
  modified = ndb.DateTimeProperty(auto_now=True)
  created_by_key = ndb.KeyProperty()
  project_keys = ndb.KeyProperty(repeated=True)
  user_keys = ndb.KeyProperty(repeated=True)
  memberships = ndb.StructuredProperty(TeamMembership, repeated=True)
  role = msgprop.EnumProperty(messages.Role)
  kind = msgprop.EnumProperty(messages.Kind, default=messages.Kind.DEFAULT)

  def __repr__(self):
    return '<Team: {}>'.format(self.ident)

  @classmethod
  def create(cls, owner, nickname, created_by, project=None,
             kind=messages.Kind.DEFAULT):
    letter = cls.get_letter_from_kind(kind)
    ident = project.ident if project else str(uuid.uuid4())[:10].replace('-', '')
    ident = '{}/{}'.format(letter, str(ident))
    key = ndb.Key('Team', ident)
    team = cls(
        key=key,
        owner_key=owner.key,
        created_by_key=created_by.key,
        nickname=nickname,
        kind=kind)
    if project:
      team.project_keys = [project.key]
    if kind != messages.Kind.DEFAULT:
      team.create_membership(created_by, role=messages.Role.ADMIN)
    return team

  @classmethod
  def get_letter_from_kind(cls, kind):
    if kind == messages.Kind.PROJECT_OWNERS:
      return 'p'
    elif kind == messages.Kind.ORG_OWNERS:
      return 'o'
    else:
      return 'd'

  @classmethod
  def get(cls, ident, kind):
    letter = cls.get_letter_from_kind(kind)
    ident = '{}/{}'.format(letter, ident)
    team = ndb.Key('Team', ident).get()
    if team is None:
      raise TeamDoesNotExistError('Team "{}" does not exist.'.format(ident))
    return team

  @classmethod
  def search(cls, owner=None, projects=None, users=None, kind=None):
    query = cls.query()
    if kind is not None:
      query = query.filter(cls.kind == kind)
    if owner is not None:
      query = query.filter(cls.owner_key == owner.key)
    if projects is not None:
      for project in projects:
        query = query.filter(cls.project_keys == project.key)
    if users is not None:
      for user in users:
        query = query.filter(cls.user_keys == user.key)
    return query.fetch()

  @property
  def owner(self):
    from jetway.owners import owners
    return owners.Owner.get_by_key(self.owner_key)

  @property
  def ident(self):
    return str(self.key.id()).split('/')[-1]

  def list_memberships(self):
    return TeamMembership.list(parent=self)

  @property
  def projects(self):
    return ndb.get_multi(self.project_keys)

  @property
  def letter(self):
    return Team.get_letter_from_kind(self.kind)

  @property
  def title(self):
    if self.kind == messages.Kind.ORG_OWNERS:
      return '{} owners'.format(self.owner.nickname)
    if self.kind == messages.Kind.PROJECT_OWNERS and self.projects:
      project = self.projects[0]
      return '{}/{} project team'.format(project.owner.nickname, project.nickname)
    return self.nickname

  def to_message(self):
    message = messages.TeamMessage()
    message.ident = self.ident
    message.title = self.title
    message.nickname = self.nickname
    message.projects = [project.to_message() for project in self.projects]
    message.description = self.description
    message.modified = self.modified
    message.memberships = [m.to_message() for m in self.memberships]
    message.title = self.title
    message.num_projects = len(self.projects)
    message.owner = self.owner.to_message()
    message.letter = self.letter
    message.role = self.role
    message.kind = self.kind
    return message

  def update(self, message):
    self.nickname = message.nickname
    self.description = message.description
    self.role = message.role
    self.put()

  def delete(self):
    self.key.delete()
#    mems = self.list_memberships()
#    keys = [mem.key for mem in mems]
#    keys.append(self.key)
#    ndb.delete_multi(keys)

  def add_project(self, project):
    if project.key in self.project_keys:
      raise ProjectConflictError('Project "{}" already exists in team.'.format(project))
    self.project_keys.append(project.key)
    self.put()

  def remove_project(self, project):
    try:
      self.project_keys.remove(project.key)
    except ValueError:
      raise ProjectConflictError('Project "{}" does not exist in team.'.format(project))
    self.put()

  def get_membership(self, user):
    for membership in self.memberships:
      if membership.user_key == user.key:
        return membership

  def create_membership(self, user, role=None, is_public=False):
    if role is None:
      role = messages.Role.READ_ONLY
#    if role is not None and self.kind != messages.Kind.PROJECT:
#      raise ValueError('Role cannot be set for non-project teams.')
    for membership in self.memberships:
      if membership.user_key == user.key:
        raise MembershipConflictError('Membership already exists.')
    membership = TeamMembership(user_key=user.key, role=role, is_public=is_public)
    self.memberships.append(membership)
    self.user_keys = [m.user_key for m in self.memberships]
    self.put()

  def delete_membership(self, user):
    # TODO: check for last remaining admin in project teams
    if self.kind == messages.Kind.ORG_OWNERS and len(self.memberships) == 1:
      raise MembershipConflictError('Cannot remove the last remaining user.')
    for i, membership in enumerate(self.memberships):
      if membership.user_key == user.key:
        del self.memberships[i]
        self.put()
        self.user_keys = [m.user_key for m in self.memberships]
        return
    raise MembershipConflictError('Membership does not exist.')

  def update_membership(self, user, role, is_public=False):
    for membership in self.memberships:
      if membership.user_key == user.key:
        membership.role = role
        membership.is_public = is_public
    self.put()
