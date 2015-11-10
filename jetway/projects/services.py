from . import service_messages
from ..buildbot import buildbot
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
      try:
        owner = owners.Owner.get(request.project.owner.nickname)
      except owners.OwnerDoesNotExistError as e:
        raise api.NotFoundError(str(e))
      project = projects.Project.create(owner, request.project.nickname,
                                        description=request.project.description,
                                        git_url=request.project.git_url,
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
      raise api.ForbiddenError('Forbidden ({})'.format(self.me))
    project.update(request.project)
    resp = service_messages.UpdateProjectResponse()
    resp.project = project.to_message()
    return resp

  @remote.method(service_messages.GetProjectRequest,
                 service_messages.GetProjectResponse)
  def get(self, request):
    project = self._get_project(request)
    if not project.can(self.me, projects.Permission.READ):
      raise api.ForbiddenError('Forbidden ({})'.format(self.me))
    resp = service_messages.GetProjectResponse()
    resp.project = project.to_message()
    return resp

  @remote.method(service_messages.DeleteProjectRequest,
                 service_messages.DeleteProjectResponse)
  def delete(self, request):
    project = self._get_project(request)
    if not project.can(self.me, projects.Permission.ADMINISTER):
      raise api.ForbiddenError('Forbidden ({})'.format(self.me))
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
      raise api.ForbiddenError('Forbidden ({})'.format(self.me))
    watcher = project.create_watcher(self.me)
    resp = service_messages.CreateWatcherResponse()
    resp.watcher = watcher.to_message()
    return resp

  @remote.method(service_messages.GetProjectRequest,
                 service_messages.ListWatchersResponse)
  def unwatch(self, request):
    project = self._get_project(request)
    if not project.can(self.me, projects.Permission.READ):
      raise api.ForbiddenError('Forbidden ({})'.format(self.me))
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
      raise api.ForbiddenError('Forbidden ({})'.format(self.me))
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
      raise api.ForbiddenError('Forbidden ({})'.format(self.me))
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
      raise api.ForbiddenError('Forbidden ({})'.format(self.me))
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
      raise api.ForbiddenError('Forbidden ({})'.format(self.me))
    project.delete_named_fileset(request.named_fileset.name)
    resp = service_messages.DeleteNamedFilesetResponse()
    return resp

  @remote.method(service_messages.ListBranchesRequest,
                 service_messages.ListBranchesResponse)
  def list_branches(self, request):
    project = self._get_project(request)
    if not project.can(self.me, projects.Permission.READ):
      raise api.ForbiddenError('Forbidden ({})'.format(self.me))
    try:
      branches = project.list_branches()
    except buildbot.Error as e:
      raise api.Error(str(e))
    resp = service_messages.ListBranchesResponse()
    resp.branches = branches
    return resp

  @remote.method(service_messages.ProjectRequest,
                 service_messages.ListCatalogsResponse)
  def list_catalogs(self, request):
    project = self._get_project(request)
    if not project.can(self.me, projects.Permission.READ):
      raise api.ForbiddenError('Forbidden ({})'.format(self.me))
    try:
      catalogs = project.list_catalogs()
    except buildbot.Error as e:
      raise api.Error(str(e))
    resp = service_messages.ListCatalogsResponse()
    resp.catalogs = [catalog.to_message(included=[]) for catalog in catalogs]
    return resp

  @remote.method(service_messages.CatalogRequest,
                 service_messages.CatalogResponse)
  def get_catalog(self, request):
    project = self._get_project(request)
    if not project.can(self.me, projects.Permission.READ):
      raise api.ForbiddenError('Forbidden ({})'.format(self.me))
    try:
      catalog = project.get_catalog(request.catalog.locale)
    except buildbot.Error as e:
      raise api.Error(str(e))
    resp = service_messages.CatalogResponse()
    resp.catalog = catalog.to_message()
    return resp

  @remote.method(service_messages.CatalogRequest,
                 service_messages.CatalogResponse)
  def update_translations(self, request):
    project = self._get_project(request)
    if not project.can(self.me, projects.Permission.READ):
      raise api.ForbiddenError('Forbidden ({})'.format(self.me))
    try:
      catalog = project.get_catalog(request.catalog.locale)
    except buildbot.Error as e:
      raise api.Error(str(e))
    catalog.update_translations(request.catalog.translations)
    resp = service_messages.CatalogResponse()
    resp.catalog = catalog.to_message()
    return resp
