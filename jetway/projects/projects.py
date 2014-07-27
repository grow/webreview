import os
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop
from jetway.avatars import avatars
from jetway.filesets import filesets
from jetway.projects import messages
from jetway.owners import owners
from jetway.teams import teams


Permission = messages.Permission


class Error(Exception):
  pass


class ProjectExistsError(Error):
  pass


class ProjectDoesNotExistError(Error):
  pass


class Cover(ndb.Model):
  content = ndb.StringProperty()

  @classmethod
  def from_message(cls, message):
    return cls(content=message.content)

  def to_message(self):
    message = messages.CoverMessage()
    message.content = self.content
    return message


class Project(ndb.Model):
  created = ndb.DateTimeProperty(auto_now_add=True)
  nickname = ndb.StringProperty()
  owner_key = ndb.KeyProperty()
  created_by_key = ndb.KeyProperty()
  description = ndb.StringProperty()
  cover = ndb.StructuredProperty(Cover)
  visibility = msgprop.EnumProperty(messages.Visibility,
                                    default=messages.Visibility.PRIVATE)

  def __repr__(self):
    return '{}/{}'.format(self.owner.nickname, self.nickname)

  @property
  def ident(self):
    return str(self.key.id())

  @classmethod
  def create(cls, owner, nickname, created_by, description=None):
    try:
      cls.get(owner, nickname)
      text = 'Project {}/{} already exists.'
      raise ProjectExistsError(text.format(owner.nickname, nickname))
    except ProjectDoesNotExistError:
      pass
    project = cls(
        owner_key=owner.key,
        created_by_key=created_by.key,
        nickname=nickname,
        description=description)
    project.put()
    teams.Team.create(owner, None,
                      created_by=created_by, project=project,
                      kind=teams.messages.Kind.PROJECT_OWNERS)
    return project

  @classmethod
  def get_by_ident(cls, ident):
    key = ndb.Key('Project', int(ident))
    project = key.get()
    if project is None:
      raise ProjectDoesNotExistError('Project {} does not exist.'.format(ident))
    return project

  @classmethod
  def get(cls, owner, nickname):
    query = cls.query()
    query = query.filter(cls.owner_key == owner.key)
    query = query.filter(cls.nickname == nickname)
    project = query.get()
    if not project:
      text = 'Project {} does not exist.'
      raise ProjectDoesNotExistError(text.format(nickname))
    return project

  @classmethod
  def search(cls, owner=None):
    query = cls.query()
    query = query.order(-cls.created)
    if owner:
      query = query.filter(cls.owner_key == owner.key)
    return query.fetch()

  def delete(self):
    from jetway.launches import launches
    team_results = teams.Team.search(projects=[self], kind=teams.messages.Kind.DEFAULT)
    launch_results = launches.Launch.search(project=self)
    fileset_results = filesets.Fileset.search(project=self)

    @ndb.transactional(retries=1, xg=True)
    def _delete_project():
      try:
        project_team = teams.Team.get(self.ident, teams.messages.Kind.PROJECT_OWNERS)
        project_team.delete()
      except teams.TeamDoesNotExistError:
        pass
      for team in team_results:
        team.remove_project(self)
      for launch in launch_results:
        launch.delete()
      for fileset in fileset_results:
        fileset.delete()
      self.key.delete()

    # Also delete filesets.
    _delete_project()

  def create_fileset(self, name):
    return filesets.Fileset.create(project=self, name=name)

  def get_fileset(self, name):
    return filesets.Fileset.get(project=self, name=name)

  def get_team(self):
    return teams.Team.get(self.ident, teams.messages.Kind.PROJECT_OWNERS)

  def search_filesets(self):
    query = filesets.Fileset.query()
    query = query.filter(filesets.Fileset.project_key == self.key)
    return query.fetch()

  def get_root(self):
    return '/filesets/{}/'.format(self.ident)

  @property
  def owner(self):
    return owners.Owner.get_by_key(self.owner_key)

  @property
  def git_url(self):
    host = os.getenv('SERVER_NAME')
    if os.getenv('SERVER_SOFTWARE').startswith('Dev'):
      port = os.getenv('SERVER_PORT')
      host = '{}:{}'.format(host, port)
    scheme = os.getenv('wsgi.url_scheme')
    return '{}://{}/{}/{}.git'.format(scheme, host, self.owner.nickname, self.nickname)

  @property
  def avatar_url(self):
    return avatars.Avatar.create_url(self)

  def to_message(self):
    message = messages.ProjectMessage()
    message.nickname = self.nickname
    message.ident = self.ident
    message.owner = self.owner.to_message()
    message.description = self.description
    message.git_url = self.git_url
    message.avatar_url = self.avatar_url
    message.visibility = self.visibility
    if self.cover:
      message.cover = self.cover.to_message()
    return message

  def update(self, message):
    self.description = message.description
    if message.cover:
      self.cover = Cover.from_message(message.cover)
    self.visibility = message.visibility
    self.put()

  def search_teams(self, users=None):
    return teams.Team.search(projects=[self], users=None)

  def search_users(self, is_public=True):
    team = self.get_team()
    users = []
    for membership in team.memberships:
      if membership.is_public == is_public:
        users.append(membership.user)
    return users

  @classmethod
  def filter(cls, results, user, permission=messages.Permission.READ):
    filtered = []
    for project in results:
      if project.can(user, permission):
        filtered.append(project)
    return filtered

  def can(self, user, permission=messages.Permission.READ):
    if self.visibility in [messages.Visibility.PUBLIC, messages.Visibility.COVER]:
      return True
    if self.owner == user:
      return True
    if not user:
      return False

    query = teams.Team.query(ndb.OR(# Project teams.
                                    ndb.AND(teams.Team.project_keys == self.key,
                                            teams.Team.user_keys == user.key),
                                    # Org Owners team.
                                    ndb.AND(teams.Team.kind == teams.messages.Kind.ORG_OWNERS,
                                            teams.Team.owner_key == self.owner.key,
                                            teams.Team.user_keys == user.key)))
    found_teams = query.fetch()
    if self.visibility == messages.Visibility.ORGANIZATION:
      return bool(found_teams)
    if self.visibility == messages.Visibility.PRIVATE:
      for team in found_teams:
        membership = team.get_membership(user)
        # Org owners have access to all projects.
        if team.kind == teams.messages.Kind.ORG_OWNERS and membership:
          return True
        # If the user is in a team that has this project, return True.
        if self.key in team.project_keys:
          return True
    return False
