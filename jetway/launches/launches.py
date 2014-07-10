from google.appengine.ext import ndb
from jetway.filesets import filesets
from jetway.projects import projects
from jetway.launches import messages
from jetway.teams import teams


class Error(Exception):
  pass


class LaunchDoesNotExistError(Error):
  pass


class LaunchExistsError(Error):
  pass


class ApprovalConflictError(Error):
  pass


class Approval(ndb.Model):
  user_key = ndb.KeyProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)

  @property
  def user(self):
    return self.user_key.get()

  def to_message(self):
    message = messages.ApprovalMessage(
        user=self.user.to_message(),
        created=self.created)
    return message


class Reviewer(ndb.Model):
  user_key = ndb.KeyProperty()
  review_required = ndb.BooleanProperty(default=False)
  created_by_key = ndb.KeyProperty()

  @property
  def created_by(self):
    return self.created_by_key.get()

  @property
  def user(self):
    return self.user_key.get()

  def to_message(self):
    message = messages.ReviewerMessage(
        user=self.user.to_message(),
        review_required=self.review_required)
    if self.created_by_key:
      message.created_by = self.created_by.to_message()
    return message


class Launch(ndb.Model):
  project_key = ndb.KeyProperty()
  ttl = ndb.DateTimeProperty()
  actual_ttl = ndb.DateTimeProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)
  created_by_key = ndb.KeyProperty()
  description = ndb.StringProperty()
  title = ndb.StringProperty()
  additional_reviewers = ndb.StructuredProperty(Reviewer, repeated=True)
  fileset_key = ndb.KeyProperty()
  approvals = ndb.StructuredProperty(Approval, repeated=True)

  @classmethod
  def create(cls, project, title, created_by, description=None):
    launch = cls(
        project_key=project.key,
        title=title,
        created_by_key=created_by.key)
    launch.put()
    if description:
      # Create comment with first description.
      pass
    return launch

  @classmethod
  def search(cls, project=None, owner=None):
    query = cls.query()
    if owner:
      project_query = projects.Project.query()
      project_query = project_query.filter(projects.Project.owner_key == owner.key)
      project_keys = project_query.fetch(keys_only=True)
      if not project_keys:
        return []
      query = query.filter(cls.project_key.IN(project_keys))
    if project:
      query = query.filter(cls.project_key == project.key)
    return query.fetch()

  @property
  def ident(self):
    return str(self.key.id())

  @classmethod
  def get_by_ident(cls, ident):
    key = ndb.Key('Launch', int(ident))
    launch = key.get()
    if launch is None:
      raise LaunchDoesNotExistError('Launch {} does not exist.'.format(ident))
    return launch

  @property
  def created_by(self):
    return self.created_by_key.get()

  @property
  def project(self):
    return self.project_key.get()

  @property
  def fileset(self):
    return self.fileset_key.get()

  @property
  def num_comments(self):
    from jetway.comments import comments
    return comments.Comment.count(parent=self, kind=comments.messages.Kind.LAUNCH)

  @property
  def reviewers(self):
    results = teams.Team.search(projects=[self.project])
    team_user_keys = set()
    for team in results:
      for membership in team.memberships:
        if membership.review_required:
          team_user_keys.add(membership.user_key)
    team_users = ndb.get_multi(list(team_user_keys))
    reviewers = []
    reviewers.extend(self.additional_reviewers)
    for user in team_users:
      reviewers.append(Reviewer(
        user_key=user.key))
    return reviewers

  def to_message(self):
    message = messages.LaunchMessage()
    message.description = self.description
    message.ident = self.ident
    message.title = self.title
    message.created = self.created
    message.created_by = self.created_by.to_message()
    message.project = self.project.to_message()
    message.ttl = self.ttl
    message.reviewers = [r.to_message() for r in self.reviewers]
    message.num_comments = self.num_comments
    message.approvals = [a.to_message() for a in self.approvals]
    if self.fileset_key:
      message.fileset = self.fileset.to_message()
    return message

  def create_approval(self, user):
    for approval in self.approvals:
      if approval.user_key == user.key:
        raise ApprovalConflictError('Approval already exists.')
    approval = Approval(user_key=user.key)
    self.approvals.append(approval)
    self.put()

  def delete_approval(self, user):
    num_approvals = len(self.approvals)
    self.approvals = [approval for approval in self.approvals
                      if approval.user_key != user.key]
    if num_approvals == len(self.approvals):
      raise ApprovalConflictError('Approval does not exist.')
    self.put()

  def update(self, message):
    if message.fileset:
      fileset = filesets.Fileset.get_by_ident(message.fileset.ident)
      self.fileset_key = fileset.key
    else:
      self.fileset_key = None
    self.title = message.title
    self.description = message.description
    self.ttl = message.ttl
    self.put()

  def diff(self, other):
    pass

  def delete(self):
    self.key.delete()
