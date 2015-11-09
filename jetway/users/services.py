from jetway import api
from jetway.users import messages
from jetway.owners import owners
from jetway.projects import projects
from jetway.users import users
from jetway.projects import watcher_messages
from protorpc import remote


class MeService(api.Service):

  @remote.method(messages.GetMeRequest,
                 messages.GetMeResponse)
  @api.me_required
  def get(self, request):
    resp = messages.GetMeResponse()
    resp.me = self.me.to_me_message()
    resp.user = resp.me
    return resp

  @remote.method(messages.SignInRequest,
                 messages.SignInResponse)
  def sign_in(self, request):
    resp = messages.SignInResponse()
    return resp

  @remote.method(messages.SignOutRequest,
                 messages.SignOutResponse)
  @api.me_required
  def sign_out(self, request):
    resp = messages.SignOutResponse()
    return resp

  @remote.method(messages.UpdateMeRequest,
                 messages.UpdateMeResponse)
  @api.me_required
  def update(self, request):
    try:
      self.me.update(request.user)
    except users.UserExistsError as e:
      raise api.ConflictError(str(e))
    resp = messages.UpdateMeResponse()
    resp.me = self.me.to_me_message()
    resp.user = resp.me
    return resp

  @remote.method(messages.SearchProjectsRequest,
                 messages.SearchProjectsResponse)
  @api.me_required
  def search_projects(self, request):
    results = self.me.search_projects()
    resp = messages.SearchProjectsResponse()
    resp.projects = [project.to_message() for project in results]
    return resp

  @remote.method(messages.SearchOrgsRequest,
                 messages.SearchOrgsResponse)
  @api.me_required
  def search_orgs(self, request):
    results = self.me.search_orgs()
    resp = messages.SearchOrgsResponse()
    resp.orgs = [org.to_message() for org in results]
    return resp

  @remote.method(watcher_messages.SearchWatchersRequest,
                 watcher_messages.SearchWatchersResponse)
  @api.me_required
  def search_watchers(self, request):
    results = self.me.search_orgs()
    resp = watcher_messages.SearchWatchersResponse()
    resp.orgs = [org.to_message() for org in results]
    return resp


class UserService(api.Service):

  def _get_project(self, request):
    try:
      if request.project.ident:
        return projects.Project.get_by_ident(request.project.ident)
      owner = owners.Owner.get(request.project.owner.nickname)
      return projects.Project.get(owner, request.project.nickname)
    except (owners.OwnerDoesNotExistError,
            projects.ProjectDoesNotExistError) as e:
      raise api.NotFoundError(str(e))

  @remote.method(messages.SearchOrgsRequest,
                 messages.SearchOrgsResponse)
  def search_orgs(self, request):
    user = users.User.get(request.user.nickname)
    results = user.search_orgs()
    resp = messages.SearchOrgsResponse()
    resp.orgs = [org.to_message() for org in results]
    return resp

  @remote.method(messages.SearchRequest,
                 messages.SearchResponse)
  def search(self, request):
    project = self._get_project(request)
    results = project.search_users()
    resp = messages.SearchResponse()
    resp.users = [user.to_message() for user in results]
    return resp
