from . import watchers
from ..buildbot import buildbot
from ..buildbot import messages as buildbot_messages
from ..catalogs import catalogs
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop
from jetway.avatars import avatars
from jetway.filesets import filesets
from jetway.filesets import named_filesets
from jetway.owners import owners
from jetway.projects import messages
from jetway.teams import teams
from protorpc import protojson
import appengine_config
import json
import logging
import os


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
  visibility = msgprop.EnumProperty(messages.Visibility)
  built = ndb.DateTimeProperty()
  buildbot_job_id = ndb.StringProperty()
  git_url = ndb.StringProperty()

  @property
  def name(self):
    return '{}/{}'.format(self.owner.nickname, self.nickname)

  @property
  def permalink(self):
    return '{}/{}'.format(appengine_config.BASE_URL, self.name)

  @property
  def name_padded(self):
    return '{} / {}'.format(self.owner.nickname, self.nickname)

  def __repr__(self):
    return self.name

  @property
  def computed_visibility(self):
    return self.visibility or messages.Visibility.DOMAIN

  @property
  def ident(self):
    return str(self.key.id())

  @classmethod
  def search_unknown_by_buildbot(cls):
    query = cls.query()
    query = query.filter(cls.known_by_buildbot == False)
    results = query.fetch()
    return results

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
    project._create_buildbot_job()
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
  def get(cls, owner=None, nickname=None):
    query = cls.query()
    if owner is not None:
      query = query.filter(cls.owner_key == owner.key)
    query = query.filter(cls.nickname == nickname)
    project = query.get()
    if not project:
      text = 'Project {} does not exist.'
      raise ProjectDoesNotExistError(text.format(nickname))
    return project

  @classmethod
  def search(cls, owner=None, order=None):
    query = cls.query()
    if order is None:
      query = query.order(-cls.created)
    elif order == messages.Order.NAME:
      query = query.order(-cls.nickname)
    if owner:
      query = query.filter(cls.owner_key == owner.key)
    return query.fetch()

  def delete(self):
    from jetway.launches import launches
    team_results = teams.Team.search(
        projects=[self],
        kind=teams.messages.Kind.DEFAULT)
    launch_results = launches.Launch.search(project=self)
    fileset_results = filesets.Fileset.search(project=self)

    @ndb.transactional(retries=1, xg=True)
    def _delete_project():
      try:
        project_team = teams.Team.get(
            self.ident, teams.messages.Kind.PROJECT_OWNERS)
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

  def create_fileset(self, name, commit=None):
    return filesets.Fileset.create(project=self, name=name, commit=commit)

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
  def avatar_url(self):
    return avatars.Avatar.create_url(self)

  @property
  def url(self):
    return '{}/{}'.format(appengine_config.BASE_URL, self.name)

  def to_message(self):
    message = messages.ProjectMessage()
    message.name = self.name
    message.nickname = self.nickname
    message.ident = self.ident
    message.owner = self.owner.to_message()
    message.description = self.description
    message.avatar_url = self.avatar_url
    message.visibility = self.visibility
    if self.cover:
      message.cover = self.cover.to_message()
    message.built = self.built
    return message

  def update(self, message):
    self.description = message.description
    if message.cover:
      self.cover = Cover.from_message(message.cover)
    self.visibility = message.visibility
    self.put()

  def search_teams(self, users=None):
    return teams.Team.search(projects=[self], users=None)

  def list_users_to_notify(self):
    return self.search_users(is_public=None)

  def search_users(self, is_public=True):
    team = self.get_team()
    users = []
    for membership in team.memberships:
      if (is_public is None
          or membership.is_public == is_public):
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
    if not user:
      return False
    # TODO: Implement proper domain-level access controls.
    username, domain = user.email.split('@')
    if username in appengine_config.DOMAIN_ACCESS_USERS:
      return True
    if (appengine_config.DEFAULT_USER_DOMAINS and
        domain in appengine_config.DEFAULT_USER_DOMAINS):
      return True
    # Permit the owner.
    if self.owner == user:
      return True
    # Permit domain users.
    if (appengine_config.DEFAULT_USER_DOMAINS
        and self.computed_visibility == messages.Visibility.DOMAIN
        and user.email.split('@')[-1] in appengine_config.DEFAULT_USER_DOMAINS):
      return
    if self.computed_visibility in [messages.Visibility.PUBLIC, messages.Visibility.COVER]:
      if appengine_config.DEFAULT_USER_DOMAINS:
        return domain in appengine_config.DEFAULT_USER_DOMAINS
      else:
        return True
    query = teams.Team.query(ndb.OR(# Project teams.
                                    ndb.AND(teams.Team.project_keys == self.key,
                                            teams.Team.user_keys == user.key),
                                    # Org Owners team.
                                    ndb.AND(teams.Team.kind == teams.messages.Kind.ORG_OWNERS,
                                            teams.Team.owner_key == self.owner.key,
                                            teams.Team.user_keys == user.key)))
    found_teams = query.fetch()
    # Permit users part of the project's organization.
    if self.computed_visibility == messages.Visibility.ORGANIZATION:
      return bool(found_teams)
    if self.computed_visibility in [messages.Visibility.PRIVATE, messages.Visibility.DOMAIN]:
      # TODO: Remove this once exposing default permissions in UI.
      if (appengine_config.DEFAULT_USER_DOMAINS
          and user.email.split('@')[-1] in appengine_config.DEFAULT_USER_DOMAINS):
        return True
      for team in found_teams:
        membership = team.get_membership(user)
        if not membership:
          continue
        # Org owners have access to all projects.
        if team.kind == teams.messages.Kind.PROJECT_OWNERS:
          return True
        elif team.kind == teams.messages.Kind.ORG_OWNERS:
          return True
        # If the user is in a team that has this project, return True.
        if self.key in team.project_keys:
          return True
    return False

  def create_watcher(self, user):
    return watchers.Watcher.create(project=self, user=user)

  def get_watcher(self, user):
    return watchers.Watcher.get(project=self, user=user)

  def delete_watcher(self, user):
    existing = self.get_watcher(user)
    if existing:
      existing.delete()

  def list_watchers(self):
    return watchers.Watcher.search(project=self)

  def create_named_fileset(self, name, branch):
    return named_filesets.NamedFileset.create(
        project=self, branch=branch, name=name)

  def delete_named_fileset(self, name):
    named_fileset = named_filesets.NamedFileset.get(name)
    if named_fileset is None:
      raise Error('Named fileset does not exist.')
    named_fileset.delete()
    return

  def list_named_filesets(self):
    return named_filesets.NamedFileset.search(project=self)

  def _create_buildbot_job(self):
    bot = buildbot.Buildbot()
    try:
      resp = bot.create_job(
          git_url=self.git_url,
          remote=self.permalink)
      self.buildbot_job_id = str(resp['job_id'])
      self.put()
    except buildbot.Error:
      logging.exception('Buildbot connection error.')

  def list_branches(self):
    bot = buildbot.Buildbot()
    data = bot.list_branches(self.buildbot_job_id)
    results = []
    for branch_data in data:
      branch_data = json.dumps(branch_data)
      message_class = buildbot_messages.BranchMessage
      branch_message = protojson.decode_message(message_class, branch_data)
      results.append(branch_message)
    return results

  def list_catalogs(self):
    bot = buildbot.Buildbot()
    items = bot.get_contents(self.buildbot_job_id, path='/translations/')
    catalog_objs = []
    for item in items:
      if item['type'] == 'dir':
        catalog = self.get_catalog(locale=item['name'])
        catalog_objs.append(catalog)
    return catalog_objs

  def get_catalog(self, locale):
    return catalogs.Catalog(project=self, locale=locale)
