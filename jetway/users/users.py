import random
from google.appengine.ext import ndb
from jetway.avatars import avatars
from jetway.files import files
from jetway.teams import teams
from jetway.users import messages
from webapp2_extras import security
from webapp2_extras.appengine.auth import models


class Error(Exception):
  pass


class UserDoesNotExistError(Error):
  pass


class UserExistsError(Error):
  pass


class BaseUser(models.User):
  email = ndb.StringProperty()

  def user_id(self):
    # Provides compatibility with oauth2client.
    return str(self.key.id())

  @classmethod
  def get_by_ident(cls, ident):
    user = cls.get_by_id(int(ident))
    if user is None:
      raise UserDoesNotExistError()
    return user

  @classmethod
  def get_by_email(cls, email):
   return cls.query(cls.email == email).get()

  @classmethod
  def get_or_create_by_email(cls, email):
   found_user = cls.query(cls.email == email).get()
   if found_user is not None:
     return found_user
   # Instead of using the email address for the nickname, strip the
   # domain and use the username. If another user already has the same
   # username, append some numbers and try again.
   username = cls.create_unique_username(email)
   return cls.create(username, email=email)

  @classmethod
  def get_multi_by_email(cls, emails):
    return cls.query(cls.email.IN(emails))

  def delete(self):
    name = self.__class__.__name__
    self.__class__.unique_model.delete_multi([
        '{}.auth_id:{}'.format(name, auth_id) for auth_id in self.auth_ids
    ])
    self.key.delete()

  @classmethod
  def create_unique_username(cls, email):
   username = email.split('@')[0]
   try:
     existing_user = cls.get(username)
   except UserDoesNotExistError:
     return username
   while existing_user is not None:
     num = int(random.random() * 1000)
     username = '{}{}'.format(username, num)
     try:
       existing_user = cls.get(username)
     except UserDoesNotExistError:
       return username
   return username


class User(BaseUser):

  nickname = ndb.StringProperty()
  description = ndb.StringProperty()
  location = ndb.StringProperty()
  website_url = ndb.StringProperty()
  hashed_git_password = ndb.StringProperty()

  def __repr__(self):
    return str(self)

  def __str__(self):
    return self.nickname or self.email

  @classmethod
  def create(cls, nickname, **kwargs):
    auth_id = 'self:{}'.format(nickname)
    success, errors_or_user = cls.create_user(auth_id, nickname=nickname, **kwargs)
    if not success:
      raise UserExistsError('User "{}" already exists.'.format(nickname))
    return errors_or_user

  @classmethod
  def get(cls, nickname):
    query = cls.query()
    query = query.filter(cls.nickname == nickname)
    user = query.get()
    if user is None:
      raise UserDoesNotExistError('User "{}" not found.'.format(nickname))
    return user

  @property
  def ident(self):
    return str(self.key.id())

  def to_message(self):
    message = messages.UserMessage()
    if self.nickname:
      message.nickname = self.nickname
    message.ident = self.ident
    message.avatar_url = self.avatar_url
    message.description = self.description
    message.location = self.description
    message.website_url = self.website_url
    message.email = self.email
    return message

  def to_me_message(self):
    message = self.to_message()
    message.email = self.email
    return message

  @property
  def avatar_url(self):
    return avatars.Avatar.create_url(self)

  @classmethod
  def get_response_for_avatar(cls, req_headers, letter, ident):
    if_none_match = req_headers.get('If-None-Match')
    resp_headers = {}
    status = 200
    content = None
    try:
      avatar = avatars.Avatar.get(letter, ident)
      try:
        resp_headers = avatar.get_headers(req_headers)
      except files.FileNotFoundError:
        resp_headers, content = avatars.Avatar.generate(ident)
    except avatars.AvatarDoesNotExistError:

      if letter == 'u':
        try:
          user = cls.get_by_ident(ident)
          # User has already gone through the OAuth2 flow into Google.
          if hasattr(user, 'picture'):
            status = 302
            resp_headers['Location'] = user.picture
          # User has never signed in, use a default avatar.
          else:
            resp_headers, content = avatars.Avatar.generate(ident)
        except UserDoesNotExistError:
          status = 404
      elif letter in ['p', 'o']:
        resp_headers, content = avatars.Avatar.generate(ident)

    if if_none_match and if_none_match == resp_headers.get('ETag'):
      status = 304
    return status, resp_headers, content

  def update(self, message):
    try:
      if User.get(message.nickname) != self:
        raise UserExistsError('Nickname already in use.')
    except UserDoesNotExistError:
      pass
    self.email = message.email
    self.nickname = message.nickname
    self.description = message.description
    self.location = message.location
    self.website_url = message.website_url
    self.put()

  def search_teams(self):
    query = teams.Team.query()
    query = query.filter(teams.Team.user_keys == self.key)
    return query.fetch()

  def search_orgs(self):
    team_ents = self.search_teams()
    org_keys = list(set([team.owner_key for team in team_ents
                         if team.kind != teams.messages.Kind.PROJECT_OWNERS]))
    return filter(None, ndb.get_multi(org_keys))

  def search_projects(self):
    team_ents = self.search_teams()
    project_keys = []
    for team in team_ents:
      project_keys += team.project_keys
    team_projects = ndb.get_multi(list(set(project_keys)))
    from jetway.projects import projects
    user_projects = projects.Project.search(owner=self)
    results = filter(None, team_projects)
    for project in user_projects:
      if project not in results:
        results.append(project)
    results = sorted(results, key=lambda project: project.nickname)
    return results
