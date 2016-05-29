from . import watchers
from ..buildbot import buildbot
from ..buildbot import messages as buildbot_messages
from ..catalogs import catalogs
from ..groups import groups
from ..groups import messages as group_messages
from ..policies import policies
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop
from app.avatars import avatars
from app.filesets import filesets
from app.filesets import named_filesets
from app.owners import owners
from app.projects import messages
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


class GitIntegrationError(Error):
  pass


class Project(ndb.Model):
  created = ndb.DateTimeProperty(auto_now_add=True)
  nickname = ndb.StringProperty()
  owner_key = ndb.KeyProperty()
  created_by_key = ndb.KeyProperty()
  description = ndb.StringProperty()
  built = ndb.DateTimeProperty()
  buildbot_job_id = ndb.StringProperty()
  git_url = ndb.StringProperty()
  group_key = ndb.KeyProperty()
  translation_branch = ndb.StringProperty()
  buildbot_git_status = msgprop.EnumProperty(messages.BuildbotGitStatus)

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
  def ident(self):
    return str(self.key.id())

  @classmethod
  def create(cls, owner, nickname, created_by, description=None, git_url=None):
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
        git_url=git_url,
        description=description)
    project.put()
    project._init_default_group()
    project._update_buildbot_job(project.git_url)
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

  def _update_buildbot_job(self, git_url):
    if self.git_url == git_url and self.buildbot_job_id:
      return
    if not git_url:
      self.buildbot_job_id = None
      self.put()
      return
    logging.info('Buildbot URL update {} -> {}'.format(self, git_url))
    bot = buildbot.Buildbot()
    try:
      resp = bot.create_job(
          git_url=git_url,
          remote=self.permalink)
      self.buildbot_job_id = str(resp['job_id'])
      text = 'Buildbot job ID update {} -> {}'
      logging.info(text.format(self, self.buildbot_job_id))
      self.put()
    except buildbot.Error:
      logging.exception('Buildbot connection error.')

  def _init_default_group(self):
    group = groups.Group.create(self)
    if appengine_config.DEFAULT_DOMAIN:
      mem_message = group_messages.MembershipMessage(
          domain=appengine_config.DEFAULT_DOMAIN)
      group.create_membership(mem_message)
    self.group_key = group.key
    self.put()
    return group

  @classmethod
  def search(cls, owner=None, order=None):
    query = cls.query()
    if order is None:
      query = query.order(-cls.created)
    elif order == messages.Order.NAME:
      query = query.order(-cls.nickname)
    if owner:
      if isinstance(owner, list):
        query = query.filter(cls.owner_key.IN([o.key for o in owner]))
      else:
        query = query.filter(cls.owner_key == owner.key)
    return query.fetch()

  def delete(self):
    from app.launches import launches
    launch_results = launches.Launch.search(project=self)
    fileset_results = filesets.Fileset.search(project=self)

    @ndb.transactional(retries=1, xg=True)
    def _delete_project():
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
  def group(self):
    def _create_group():
      group = groups.Group.create()
      self.group_key = group.key
      self.put()
      group.project = self
      return group
    if not self.group_key:
      return _create_group()
    group = self.group_key.get()
    if group is None:
      return _create_group()
    group.project = self
    return group

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
    message.git_url = self.git_url
    message.buildbot_job_id = self.buildbot_job_id
    message.built = self.built
    message.translation_branch = self.translation_branch
    return message

  def update(self, message):
    self.description = message.description
    self.translation_branch = message.translation_branch
    self._update_buildbot_job(message.git_url)
    self.git_url = message.git_url
    self.put()

  def transfer_owner(self, owner):
    self.owner_key = owner.key
    self.put()

  def list_users_to_notify(self):
    return self.search_users(is_public=None)

  def search_users(self, is_public=True):
    users = []
    for membership in self.group.memberships:
      if membership.user_key:
        users.append(membership.user)
    return users

  @classmethod
  def filter(cls, results, user, permission=messages.Permission.READ):
    filtered = []
    for project in results:
      policy = policies.ProjectPolicy(user, project)
      if policy.can_read():
        filtered.append(project)
    return filtered

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

  def verify_repo_status(self):
    if not self.buildbot_job_id:
      raise GitIntegrationError('Git repository not initialized.')

  def list_branches(self):
    self.verify_repo_status()
    bot = buildbot.Buildbot()
    job = bot.get_job(self.buildbot_job_id)['job']
    results = []
    for ref, data in job['ref_map'].iteritems():
      name = ref.replace('refs/heads/', '')
      commit = buildbot_messages.CommitMessage(sha=data['sha'])
      ident = self.ident + ':branch:' + name
      branch_message = buildbot_messages.BranchMessage(
          name=name,
          commit=commit,
          ident=ident)
      results.append(branch_message)
    results = sorted(results, key=lambda message: message.name)
    return results

  def list_catalogs(self, ref=None):
    self.verify_repo_status()
    bot = buildbot.Buildbot()
    items = bot.get_contents(
        self.buildbot_job_id,
        path='/translations/',
        ref=ref)
    catalog_objs = []
    for item in items:
      if item['type'] == 'dir':
        catalog = self.get_catalog(locale=item['name'])
        catalog_objs.append(catalog)
    return catalog_objs

  def get_catalog(self, locale, ref=None):
    self.verify_repo_status()
    return catalogs.Catalog(project=self, locale=locale, ref=ref)
