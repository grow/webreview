from .api_errors import *
from .owners import owners
from .projects import projects
from .users import users
from protorpc import remote
from webapp2_extras import auth as webapp2_auth
import appengine_config
import os
import webapp2


class Service(remote.Service):

  def get_project(self, request):
    try:
      if request.project.ident:
        return projects.Project.get_by_ident(request.project.ident)
      else:
        owner = owners.Owner.get(request.project.owner.nickname)
        return projects.Project.get(owner, request.project.nickname)
    except (owners.OwnerDoesNotExistError,
            projects.ProjectDoesNotExistError) as e:
      raise NotFoundError(str(e))

  def get_owner(self, request):
    try:
      if request.owner.nickname:
        return owners.Owner.get(request.owner.nickname)
      elif request.owner.ident:
        return owners.Owner.get_by_ident(request.owner.ident)
    except owners.OwnerDoesNotExistError as e:
      raise NotFoundError(str(e))

  @property
  def request(self):
    request = webapp2.Request(environ=dict(os.environ))
    request.app = webapp2.WSGIApplication(config=appengine_config.WEBAPP2_AUTH_CONFIG)
    return request

  @webapp2.cached_property
  def auth(self):
    return webapp2_auth.get_auth(request=self.request)

  @webapp2.cached_property
  def is_authorized_buildbot_request(self):
    return ('WebReview-Api-Key' in self.request.headers
            and appengine_config.BUILDBOT_API_KEY is not None
            and self.request.headers['WebReview-Api-Key'] == appengine_config.BUILDBOT_API_KEY)

  @webapp2.cached_property
  def me(self):
    user_dict = self.auth.get_user_by_session()
    if user_dict:
      return users.User.get_by_auth_id(str(user_dict['user_id']))


def me_required(method):
  def wrapped_func(*args, **kwargs):
    self = args[0]
    if self.me is None:
      raise UnauthorizedError('You must be signed in.')
    return method(*args, **kwargs)
  return wrapped_func
