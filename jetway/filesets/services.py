from jetway import api
from jetway.filesets import filesets
from jetway.filesets import messages
from jetway.owners import owners
from jetway.projects import projects
from jetway.users import users
from protorpc import remote
import appengine_config
import endpoints
import os
import webapp2


# Command-line Grow SDK (API project: grow-prod).
_jetway_client = (
    '578372381550-jfl3hdlf1q5rgib94pqsctv1kgkflu1a'
    '.apps.googleusercontent.com')

endpoints_api = endpoints.api(
    name='webreview',
    version='v0',
    allowed_client_ids=[_jetway_client, endpoints.API_EXPLORER_CLIENT_ID],
    scopes=[
        endpoints.EMAIL_SCOPE,
        'https://www.googleapis.com/auth/plus.me',
    ],
)

new_endpoints_api = endpoints.api(
    name='webreview',
    version='v1',
    allowed_client_ids=[_jetway_client, endpoints.API_EXPLORER_CLIENT_ID],
    scopes=[
        endpoints.EMAIL_SCOPE,
        'https://www.googleapis.com/auth/plus.me',
    ],
)

legacy_endpoints_api = endpoints.api(
    name='jetway',
    version='v0',
    allowed_client_ids=[_jetway_client, endpoints.API_EXPLORER_CLIENT_ID],
    scopes=[
        endpoints.EMAIL_SCOPE,
        'https://www.googleapis.com/auth/plus.me',
    ],
)


class BaseFilesetService(object):

  def _is_authorized_buildbot(self):
    key = 'WebReview-Api-Key'
    request = webapp2.Request(environ=dict(os.environ))
    if (key in request.headers
        and appengine_config.BUILDBOT_API_KEY is not None):
      if request.headers[key] != appengine_config.BUILDBOT_API_KEY:
        raise api.BadRequestError('Invalid API key.')
      return True
    return False

  def _get_project(self, request):
    try:
      if request.fileset.project and request.fileset.project.ident:
        return projects.Project.get_by_ident(request.fileset.project.ident)
      elif request.fileset.project.owner:
        o = owners.Owner.get(request.fileset.project.owner.nickname)
        return projects.Project.get(o, request.fileset.project.nickname)
      else:
        raise api.BadRequestError('Missing required field: project.')
    except (projects.ProjectDoesNotExistError,
            owners.OwnerDoesNotExistError) as e:
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
      if request.fileset.project.ident:
        project = projects.Project.get_by_ident(request.fileset.project.ident)
      else:
        owner = owners.Owner.get(request.fileset.project.owner.nickname)
        project = projects.Project.get(owner, request.fileset.project.nickname)
    else:
      project = None
    if (not self._is_authorized_buildbot()
        and not project.can(self.me, projects.Permission.READ)):
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

#  @remote.method(messages.FinalizeFilesetRequest,
#                 messages.FinalizeFilesetResponse)
#  def finalize(self, request):
#    fileset = self._get_fileset(request)
#    fileset.update(request.fileset)
#    resp = messages.FinalizeFilesetResponse()
#    resp.fileset = fileset.to_message()
#    return resp

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

  def _get_me(self, request):
    if self._is_authorized_buildbot():
      email = appengine_config.BUILDBOT_SERVICE_ACCOUNT
    else:
      user = endpoints.get_current_user()
      if user is None:
        raise api.UnauthorizedError('You must be logged in to do this.')
      email = user.email()
    return users.User.get_by_email(email)

  def _get_or_create_fileset(self, request, me):
    allow_fileset_by_commit = bool(request.fileset.commit)
    p = self._get_project(request)
    try:
      if allow_fileset_by_commit:
        return filesets.Fileset.get(project=p, commit=request.fileset.commit)
      elif request.fileset.ident:
        return filesets.Fileset.get_by_ident(request.fileset.ident)
      else:
        p = self._get_project(request)
        return p.get_fileset(request.fileset.name)
    except filesets.FilesetDoesNotExistError:
      return filesets.Fileset.create(
          p, name=request.fileset.name, commit=request.fileset.commit, created_by=me)

  @endpoints.method(messages.FinalizeRequest,
                    messages.FinalizeResponse)
  def finalize(self, request):
    me = self._get_me(request)
    fileset = self._get_or_create_fileset(request, me)
    fileset.finalize()
    resp = messages.FinalizeResponse()
    resp.fileset = fileset.to_message()
    return resp

  @endpoints.method(messages.SignRequestsRequest,
                    messages.SignRequestsResponse)
  def sign_requests(self, request):
    me = self._get_me(request)
    fileset = self._get_or_create_fileset(request, me)
    if (not self._is_authorized_buildbot()
        and not fileset.project.can(me, projects.Permission.WRITE)):
      raise api.ForbiddenError('Forbidden.')
    signed_reqs = fileset.sign_requests(request.unsigned_requests)
    resp = messages.SignRequestsResponse()
    resp.fileset = fileset.to_message()
    resp.signed_requests = signed_reqs
    return resp


@legacy_endpoints_api
class LegacyRequestSigningService(RequestSigningService):
  pass


@new_endpoints_api
class NewRequestSigningService(RequestSigningService):
  pass
