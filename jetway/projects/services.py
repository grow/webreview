from . import service_messages
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

  @remote.method(service_messages.CreateProjectRequest,
                 service_messages.CreateProjectResponse)
  def create(self, request):
    try:
      owner = owners.Owner.get(request.project.owner.nickname)
      project = projects.Project.create(owner, request.project.nickname,
                                        description=request.project.description,
                                        created_by=self.me)
    except projects.ProjectExistsError as e:
      raise api.ConflictError(str(e))
    resp = service_messages.CreateProjectResponse()
    resp.project = project.to_message()
    return resp

  @remote.method(service_messages.SearchProjectRequest,
                 service_messages.SearchProjectResponse)
  def search(self, request):
    if request.project and request.project.owner:
      owner = owners.Owner.get(request.project.owner.nickname)
    else:
      owner = None
    results = projects.Project.search(owner=owner, order=messages.Order.NAME)
    results = projects.Project.filter(results, self.me)
    results = sorted(results, key=lambda project: project.name)
    resp = service_messages.SearchProjectResponse()
    resp.projects = [project.to_message() for project in results]
    return resp

  @remote.method(service_messages.UpdateProjectRequest,
                 service_messages.UpdateProjectResponse)
  def update(self, request):
    project = self._get_project(request)
    if not project.can(self.me, projects.Permission.ADMINISTER):
      raise api.ForbiddenError('Forbidden.')
    project.update(request.project)
    resp = service_messages.UpdateProjectResponse()
    resp.project = project.to_message()
    return resp

  @remote.method(service_messages.GetProjectRequest,
                 service_messages.GetProjectResponse)
  def get(self, request):
    project = self._get_project(request)
    if not project.can(self.me, projects.Permission.READ):
      raise api.ForbiddenError('Forbidden.')
    resp = service_messages.GetProjectResponse()
    resp.project = project.to_message()
    return resp

  @remote.method(service_messages.DeleteProjectRequest,
                 service_messages.DeleteProjectResponse)
  def delete(self, request):
    project = self._get_project(request)
    if not project.can(self.me, projects.Permission.ADMINISTER):
      raise api.ForbiddenError('Forbidden.')
    project.delete()
    resp = service_messages.DeleteProjectResponse()
    return resp

  @remote.method(service_messages.CanRequest,
                 service_messages.CanResponse)
  def can(self, request):
    project = self._get_project(request)
    can = project.can(self.me, request.permission)
    resp = service_messages.CanResponse()
    resp.can = can
    return resp

  @remote.method(service_messages.GetProjectRequest,
                 service_messages.CreateWatcherResponse)
  def watch(self, request):
    project = self._get_project(request)
    if not project.can(self.me, projects.Permission.READ):
      raise api.ForbiddenError('Forbidden.')
    watcher = project.create_watcher(self.me)
    resp = service_messages.CreateWatcherResponse()
    resp.watcher = watcher.to_message()
    return resp

  @remote.method(service_messages.GetProjectRequest,
                 service_messages.ListWatchersResponse)
  def unwatch(self, request):
    project = self._get_project(request)
    if not project.can(self.me, projects.Permission.READ):
      raise api.ForbiddenError('Forbidden.')
    project.delete_watcher(self.me)
    watchers = project.list_watchers()
    resp = service_messages.ListWatchersResponse()
    resp.watchers = [watcher.to_message() for watcher in watchers]
    return resp

  @remote.method(service_messages.ListWatchersRequest,
                 service_messages.ListWatchersResponse)
  def list_watchers(self, request):
    project = self._get_project(request)
    if not project.can(self.me, projects.Permission.READ):
      raise api.ForbiddenError('Forbidden.')
    watchers = project.list_watchers()
    resp = service_messages.ListWatchersResponse()
    resp.watching = any(self.me == watcher.user for watcher in watchers)
    resp.watchers = [watcher.to_message() for watcher in watchers]
    return resp

  @remote.method(service_messages.ListNamedFilesetsRequest,
                 service_messages.ListNamedFilesetsResponse)
  def list_named_filesets(self, request):
    project = self._get_project(request)
    if not project.can(self.me, projects.Permission.READ):
      raise api.ForbiddenError('Forbidden.')
    named_filesets = project.list_named_filesets()
    resp = service_messages.ListNamedFilesetsRequest()
    resp.named_filesets = [named_fileset.to_message()
                           for named_fileset in named_filesets]
    return resp

  @remote.method(service_messages.CreateNamedFilesetRequest,
                 service_messages.CreateNamedFilesetResponse)
  def create_named_fileset(self, request):
    project = self._get_project(request)
    if not project.can(self.me, projects.Permission.WRITE):
      raise api.ForbiddenError('Forbidden.')
    named_fileset = project.create_named_fileset(
        request.named_fileset.name, request.named_fileset.branch)
    resp = service_messages.CreateNamedFilesetResponse()
    resp.named_fileset = named_fileset.to_message()
    return resp

  @remote.method(service_messages.DeleteNamedFilesetRequest,
                 service_messages.DeleteNamedFilesetResponse)
  def delete_named_fileset(self, request):
    project = self._get_project(request)
    if not project.can(self.me, projects.Permission.READ):
      raise api.ForbiddenError('Forbidden.')
    project.delete_named_fileset(request.named_fileset.name)
    resp = service_messages.DeleteNamedFilesetResponse()
    return resp
