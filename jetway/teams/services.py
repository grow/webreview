from jetway import api
from jetway.teams import teams
from jetway.owners import owners
from jetway.teams import messages
from jetway.projects import projects
from jetway.users import users
from protorpc import remote


class TeamService(api.Service):

  def _check_permission(self, team, permission):
    if team.kind == teams.messages.Kind.PROJECT_OWNERS:
      project = team.projects[0]
      if not project.can(self.me, permission):
        raise api.ForbiddenError('Forbidden.')

  def _get_projects(self, request):
    project_ents = []
    if request.team.projects:
      for project in request.team.projects:
        owner = self._get_owner(request)
        project_ents.append(self._get_project(owner, project.nickname))
    return project_ents

  def _get_user(self, request):
    if request.membership.user.ident:
      return users.User.get_by_ident(request.membership.user.ident)
    elif request.membership.user.email:
      return users.User.get_or_create_by_email(request.membership.user.email)
    else:
      return users.User.get(request.user.nickname)

  def _get_project(self, owner, nickname):
    try:
      return projects.Project.get(owner, nickname)
    except projects.ProjectDoesNotExistError as e:
      raise api.NotFoundError(str(e))

  def _get_team(self, request):
    try:
      if request.team.ident:
        return teams.Team.get(request.team.ident, request.team.kind)
      owner = self.get_owner(request)
      return owner.get_team(request.team.nickname)
    except teams.TeamDoesNotExistError as e:
      raise api.NotFoundError(str(e))

  def _get_owner(self, request):
    return owners.Owner.get(request.team.owner.nickname)

  @remote.method(
      messages.CreateTeamRequest,
      messages.CreateTeamResponse)
  def create(self, request):
    owner = self._get_owner(request)
    try:
      team = owner.create_team(request.team.nickname, created_by=self.me)
    except teams.TeamExistsError as e:
      raise api.ConflictError(str(e))
    message = messages.CreateTeamResponse()
    message.team = team.to_message()
    return message

  @remote.method(
      messages.SearchTeamRequest,
      messages.SearchTeamResponse)
  def search(self, request):
    owner = self._get_owner(request) if request.team.owner else None
    project_ents = self._get_projects(request)
    results = teams.Team.search(owner=owner, projects=project_ents, kind=request.team.kind)
    message = messages.SearchTeamResponse()
    message.teams = [team.to_message() for team in results]
    return message

  @remote.method(
      messages.DeleteTeamRequest,
      messages.DeleteTeamResponse)
  def delete(self, request):
    team = self._get_team(request)
    team.delete()
    message = messages.DeleteTeamResponse()
    return message

  @remote.method(
      messages.GetTeamRequest,
      messages.GetTeamResponse)
  def get(self, request):
    team = self._get_team(request)
    message = messages.GetTeamResponse()
    message.team = team.to_message()
    return message

  @remote.method(
      messages.UpdateTeamRequest,
      messages.UpdateTeamResponse)
  def update(self, request):
    team = self._get_team(request)
    team.update(request.team)
    message = messages.UpdateTeamResponse()
    message.team = team.to_message()
    return message

  @remote.method(
      messages.AddProjectRequest,
      messages.AddProjectResponse)
  def add_project(self, request):
    team = self._get_team(request)
    self._check_permission(team, projects.Permission.ADMINISTER)
    project = self._get_project(team.owner, request.project.nickname)
    try:
      team.add_project(project)
    except teams.ProjectConflictError as e:
      raise api.ConflictError(str(e))
    resp = messages.AddProjectResponse()
    resp.team = team.to_message()
    return resp

  @remote.method(
      messages.RemoveProjectRequest,
      messages.RemoveProjectResponse)
  def remove_project(self, request):
    owner = self.get_owner(request)
    team = owner.get_team(request.team.nickname)
    self._check_permission(team, projects.Permission.ADMINISTER)
    project = self._get_project(owner, request.project.nickname)
    try:
      team.remove_project(project)
    except teams.ProjectConflictError as e:
      raise api.ConflictError(str(e))
    resp = messages.RemoveProjectResponse()
    resp.team = team.to_message()
    return resp

  @remote.method(
      messages.CreateMembershipRequest,
      messages.CreateMembershipResponse)
  def create_membership(self, request):
    team = self._get_team(request)
    self._check_permission(team, projects.Permission.ADMINISTER)
    user = self._get_user(request)
    try:
      team.create_membership(user, role=request.membership.role)
      resp = messages.CreateMembershipResponse()
      resp.team = team.to_message()
      return resp
    except teams.MembershipConflictError as e:
      raise api.ConflictError(str(e))

  @remote.method(
      messages.DeleteMembershipRequest,
      messages.DeleteMembershipResponse)
  def delete_membership(self, request):
    team = self._get_team(request)
    self._check_permission(team, projects.Permission.ADMINISTER)
    user = self._get_user(request)
    try:
      team.delete_membership(user)
      resp = messages.DeleteMembershipResponse()
      resp.team = team.to_message()
      return resp
    except teams.MembershipConflictError as e:
      raise api.NotFoundError(str(e))

  @remote.method(
      messages.UpdateMembershipRequest,
      messages.UpdateMembershipResponse)
  def update_membership(self, request):
    team = self._get_team(request)
    self._check_permission(team, projects.Permission.ADMINISTER)
    user = self._get_user(request)
    team.update_membership(user,
                           role=request.membership.role,
                           is_public=request.membership.is_public)
    resp = messages.UpdateMembershipResponse()
    resp.team = team.to_message()
    return resp
