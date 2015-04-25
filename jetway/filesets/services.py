from jetway import api
from jetway.filesets import filesets
from jetway.filesets import messages
from jetway.owners import owners
from jetway.projects import projects
from jetway.users import users
from protorpc import remote
import endpoints


# Command-line Grow SDK (API project: grow-prod).
_jetway_client = (
    '578372381550-jfl3hdlf1q5rgib94pqsctv1kgkflu1a'
    '.apps.googleusercontent.com')
endpoints_api = endpoints.api(
    name='jetway',
    version='v0',
    allowed_client_ids=[_jetway_client, endpoints.API_EXPLORER_CLIENT_ID],
    scopes=[
        endpoints.EMAIL_SCOPE,
        'https://www.googleapis.com/auth/plus.me',
    ],
)


class BaseFilesetService(object):

  def _get_project(self, request):
    try:
      if request.fileset.project.owner:
        o = owners.Owner.get(request.fileset.project.owner.nickname)
        return projects.Project.get(o, request.fileset.project.nickname)
      elif request.fileset.project.ident:
        return projects.Project.get_by_ident(request.fileset.project.ident)
      else:
        raise api.BadRequestError('Missing required field: project.')
    except projects.ProjectDoesNotExistError as e:
      raise api.NotFoundError(str(e))

  def _get_fileset(self, request):
    try:
      if request.fileset.ident:
        return filesets.Fileset.get_by_ident(request.fileset.ident)
      else:
        p = self._get_project(request)
        return p.get_fileset(request.fileset.name)
    except filesets.FilesetDoesNotExistError as e:
      raise api.NotFoundError(str(e))


class FilesetService(api.Service, BaseFilesetService):

  @remote.method(messages.CreateFilesetRequest,
                 messages.CreateFilesetResponse)
  def create(self, request):
    try:
      owner = owners.Owner.get(request.fileset.project.owner.nickname)
      project = projects.Project.get(owner, request.fileset.project.nickname)
      fileset = filesets.Fileset.create(project, request.fileset.name)
    except filesets.FilesetExistsError as e:
      raise api.ConflictError(str(e))
    resp = messages.CreateFilesetResponse()
    resp.fileset = fileset.to_message()
    return resp

  @remote.method(messages.DeleteFilesetRequest,
                 messages.DeleteFilesetResponse)
  def delete(self, request):
    fileset = self._get_fileset(request)
    fileset.delete()
    resp = messages.DeleteFilesetResponse()
    return resp

  @remote.method(messages.SearchFilesetRequest,
                 messages.SearchFilesetResponse)
  def search(self, request):
    if request.fileset.project:
      owner = owners.Owner.get(request.fileset.project.owner.nickname)
      project = projects.Project.get(owner, request.fileset.project.nickname)
    else:
      project = None
    if not project.can(self.me, projects.Permission.READ):
      raise api.ForbiddenError('Forbidden.')
    results = filesets.Fileset.search(project=project)
    resp = messages.SearchFilesetResponse()
    resp.filesets = [e.to_message() for e in results]
    return resp

  @remote.method(messages.GetFilesetRequest,
                 messages.GetFilesetResponse)
  def get(self, request):
    fileset = self._get_fileset(request)
    resp = messages.GetFilesetResponse()
    resp.fileset = fileset.to_message()
    return resp

  @remote.method(messages.FinalizeFilesetRequest,
                 messages.FinalizeFilesetResponse)
  def finalize(self, request):
    fileset = self._get_fileset(request)
    fileset.update(request.fileset)
    resp = messages.FinalizeFilesetResponse()
    resp.fileset = fileset.to_message()
    return resp

  @remote.method(messages.GetPageSpeedResultRequest,
                 messages.GetPageSpeedResultResponse)
  def get_pagespeed_result(self, request):
    fileset = self._get_fileset(request)
    runner = fileset.get_pagespeed_runner()
    pagespeed_result = runner.run(request.file.path)
    resp = messages.GetPageSpeedResultResponse()
    resp.pagespeed_result = pagespeed_result
    return resp


@endpoints_api
class RequestSigningService(remote.Service, BaseFilesetService):

  @endpoints.method(messages.SignRequestsRequest,
                    messages.SignRequestsResponse)
  def sign_requests(self, request):
    user = endpoints.get_current_user()
    if user is None:
      raise api.UnauthorizedError('You must be logged in to do this.')
    me = users.User.get_by_email(user.email())
    try:
      if request.fileset.ident:
        fileset = filesets.Fileset.get_by_ident(request.fileset.ident)
      else:
        p = self._get_project(request)
        fileset = p.get_fileset(request.fileset.name)
    except filesets.FilesetDoesNotExistError:
      p = self._get_project(request)
      fileset = filesets.Fileset.create(p, request.fileset.name, me)
    if not fileset.project.can(me, projects.Permission.WRITE):
      raise api.ForbiddenError('Forbidden.')
    signed_reqs = fileset.sign_requests(request.unsigned_requests)
    resp = messages.SignRequestsResponse()
    resp.fileset = fileset.to_message()
    resp.signed_requests = signed_reqs
    return resp
