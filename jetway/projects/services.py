from protorpc import remote
from jetway import api
from jetway.owners import owners
from jetway.projects import projects
from jetway.projects import messages


class ProjectService(api.Service):

  def _get_project(self, request):
    try:
      if request.project.ident:
        return projects.Project.get_by_ident(request.project.ident)
      owner = owners.Owner.get(request.project.owner.nickname)
      return projects.Project.get(owner, request.project.nickname)
    except (owners.OwnerDoesNotExistError,
            projects.ProjectDoesNotExistError) as e:
      raise api.NotFoundError(str(e))

  @remote.method(messages.CreateProjectRequest,
                 messages.CreateProjectResponse)
  def create(self, request):
    try:
      owner = owners.Owner.get(request.project.owner.nickname)
      project = projects.Project.create(owner, request.project.nickname,
                                        description=request.project.description,
                                        created_by=self.me)
    except projects.ProjectExistsError as e:
      raise api.ConflictError(str(e))
    resp = messages.CreateProjectResponse()
    resp.project = project.to_message()
    return resp

  @remote.method(messages.SearchProjectRequest,
                 messages.SearchProjectResponse)
  def search(self, request):
    if request.project and request.project.owner:
      owner = owners.Owner.get(request.project.owner.nickname)
    else:
      owner = None
    results = projects.Project.search(owner=owner)
    results = projects.Project.filter(results, self.me)
    resp = messages.SearchProjectResponse()
    resp.projects = [project.to_message() for project in results]
    return resp

  @remote.method(messages.UpdateProjectRequest,
                 messages.UpdateProjectResponse)
  def update(self, request):
    project = self._get_project(request)
    if not project.can(self.me, projects.Permission.ADMINISTER):
      raise api.ForbiddenError('Forbidden.')
    project.update(request.project)
    resp = messages.UpdateProjectResponse()
    resp.project = project.to_message()
    return resp

  @remote.method(messages.GetProjectRequest,
                 messages.GetProjectResponse)
  def get(self, request):
    project = self._get_project(request)
#    if not project.can(self.me, projects.Permission.READ):
#      raise api.ForbiddenError('Forbidden.')
    resp = messages.GetProjectResponse()
    resp.project = project.to_message()
    return resp

  @remote.method(messages.DeleteProjectRequest,
                 messages.DeleteProjectResponse)
  def delete(self, request):
    project = self._get_project(request)
    if not project.can(self.me, projects.Permission.ADMINISTER):
      raise api.ForbiddenError('Forbidden.')
    project.delete()
    resp = messages.DeleteProjectResponse()
    return resp

  @remote.method(messages.CanRequest,
                 messages.CanResponse)
  def can(self, request):
    project = self._get_project(request)
    can = project.can(self.me, request.permission)
    resp = messages.CanResponse()
    resp.can = can
    return resp
