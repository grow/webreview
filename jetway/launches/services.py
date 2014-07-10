from jetway import api
from jetway.launches import launches
from jetway.owners import owners
from jetway.launches import messages
from jetway.projects import projects
from jetway.users import users
from protorpc import remote


class LaunchService(api.Service):

  def _get_user(self, request):
    if request.membership.user.email:
      return users.User.get_or_create_by_email(request.membership.user.email)
    elif request.membership.user.ident:
      return users.User.get_by_ident(request.membership.user.ident)
    else:
      return users.User.get(request.user.nickname)

  def _get_owner(self, request):
    return owners.Owner.get(request.launch.project.owner.nickname)

  def _get_project(self, request):
    try:
      owner = self._get_owner(request)
      nickname = request.launch.project.nickname
      return projects.Project.get(owner, nickname)
    except projects.ProjectDoesNotExistError as e:
      raise api.NotFoundError(str(e))

  def _get_launch(self, request):
    try:
      if request.launch.ident:
        return launches.Launch.get_by_ident(request.launch.ident)
      owner = self.get_owner(request)
      return owner.get_launch(request.launch.nickname)
    except launches.LaunchDoesNotExistError as e:
      raise api.NotFoundError(str(e))

  @remote.method(
      messages.CreateLaunchRequest,
      messages.CreateLaunchResponse)
  def create(self, request):
    project = self._get_project(request)
    try:
      launch = launches.Launch.create(
          project=project,
          title=request.launch.title,
          description=request.launch.description,
          created_by=self.me)
    except launches.LaunchExistsError as e:
      raise api.ConflictError(str(e))
    message = messages.CreateLaunchResponse()
    message.launch = launch.to_message()
    return message

  @remote.method(
      messages.SearchLaunchRequest,
      messages.SearchLaunchResponse)
  def search(self, request):
    owner = self._get_owner(request) if request.launch.project.owner else None
    project = self._get_project(request) if request.launch.project.nickname else None
    results = launches.Launch.search(owner=owner, project=project)
    message = messages.SearchLaunchResponse()
    message.launches = [launch.to_message() for launch in results]
    return message

  @remote.method(
      messages.DeleteLaunchRequest,
      messages.DeleteLaunchResponse)
  def delete(self, request):
    owner = self.get_owner(request)
    launch = owner.get_launch(request.launch.nickname)
    launch.delete()
    message = messages.DeleteLaunchResponse()
    return message

  @remote.method(
      messages.GetLaunchRequest,
      messages.GetLaunchResponse)
  def get(self, request):
    launch = self._get_launch(request)
    message = messages.GetLaunchResponse()
    message.launch = launch.to_message()
    return message

  @remote.method(
      messages.UpdateLaunchRequest,
      messages.UpdateLaunchResponse)
  def update(self, request):
    launch = self._get_launch(request)
    launch.update(request.launch)
    message = messages.UpdateLaunchResponse()
    message.launch = launch.to_message()
    return message

  @remote.method(
      messages.CreateApprovalRequest,
      messages.CreateApprovalResponse)
  def create_approval(self, request):
    launch = self._get_launch(request)
    launch.create_approval(self.me)
    message = messages.CreateApprovalResponse()
    message.launch = launch.to_message()
    return message

  @remote.method(
      messages.DeleteApprovalRequest,
      messages.DeleteApprovalResponse)
  def delete_approval(self, request):
    launch = self._get_launch(request)
    launch.delete_approval(self.me)
    message = messages.DeleteApprovalResponse()
    message.launch = launch.to_message()
    return message
