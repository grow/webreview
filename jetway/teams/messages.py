from protorpc import messages
from protorpc import message_types
from jetway.owners import messages as owner_messages
from jetway.projects import messages as project_messages
from jetway.users import messages as user_messages


class Role(messages.Enum):
  ADMIN = 1
  READ_ONLY = 2
  WRITE_FULL = 3
  WRITE_TRANSLATIONS = 4
  WRITE_CONTENT = 5


class Kind(messages.Enum):
  DEFAULT = 1
  ORG_OWNERS = 2
  PROJECT_OWNERS = 3


class PermissionsMessage(messages.Message):
  administer = messages.BooleanField(1, default=False)


class TeamMembershipMessage(messages.Message):
  user = messages.MessageField(user_messages.UserMessage, 1)
  role = messages.EnumField(Role, 2)
  is_public = messages.BooleanField(3)
  review_required = messages.BooleanField(4)


class TeamMessage(messages.Message):
  nickname = messages.StringField(1)
  perms = messages.MessageField(PermissionsMessage, 2)
  projects = messages.MessageField(project_messages.ProjectMessage, 3, repeated=True)
  description = messages.StringField(4)
  modified = message_types.DateTimeField(5)
  memberships = messages.MessageField(TeamMembershipMessage, 6, repeated=True)
  role = messages.EnumField(Role, 7)
  num_projects = messages.IntegerField(8)
  owner = messages.MessageField(owner_messages.OwnerMessage, 9)
  ident = messages.StringField(10)
  kind = messages.EnumField(Kind, 11)
  letter = messages.StringField(12)
  title = messages.StringField(13)


###


class CreateTeamRequest(messages.Message):
  team = messages.MessageField(TeamMessage, 1)
  owner = messages.MessageField(owner_messages.OwnerMessage, 2)


class CreateTeamResponse(messages.Message):
  team = messages.MessageField(TeamMessage, 1)


class SearchTeamRequest(messages.Message):
  team = messages.MessageField(TeamMessage, 1)
  owner = messages.MessageField(owner_messages.OwnerMessage, 2)
  project = messages.MessageField(project_messages.ProjectMessage, 3)


class SearchTeamResponse(messages.Message):
  teams = messages.MessageField(TeamMessage, 1, repeated=True)


class GetTeamRequest(messages.Message):
  team = messages.MessageField(TeamMessage, 1)
  owner = messages.MessageField(owner_messages.OwnerMessage, 2)


class GetTeamResponse(messages.Message):
  team = messages.MessageField(TeamMessage, 1)


class UpdateTeamRequest(messages.Message):
  team = messages.MessageField(TeamMessage, 1)
  owner = messages.MessageField(owner_messages.OwnerMessage, 2)


class UpdateTeamResponse(messages.Message):
  team = messages.MessageField(TeamMessage, 1)


class DeleteTeamRequest(messages.Message):
  team = messages.MessageField(TeamMessage, 1)
  owner = messages.MessageField(owner_messages.OwnerMessage, 2)
  project = messages.MessageField(project_messages.ProjectMessage, 3)


class DeleteTeamResponse(messages.Message):
  pass


class AddProjectRequest(messages.Message):
  team = messages.MessageField(TeamMessage, 1)
  owner = messages.MessageField(owner_messages.OwnerMessage, 2)
  project = messages.MessageField(project_messages.ProjectMessage, 3)


class AddProjectResponse(messages.Message):
  team = messages.MessageField(TeamMessage, 1)


class RemoveProjectRequest(messages.Message):
  team = messages.MessageField(TeamMessage, 1)
  owner = messages.MessageField(owner_messages.OwnerMessage, 2)
  project = messages.MessageField(project_messages.ProjectMessage, 3)


class RemoveProjectResponse(messages.Message):
  team = messages.MessageField(TeamMessage, 1)


class CreateMembershipRequest(messages.Message):
  team = messages.MessageField(TeamMessage, 1)
  owner = messages.MessageField(owner_messages.OwnerMessage, 2)
  membership = messages.MessageField(TeamMembershipMessage, 3)


class CreateMembershipResponse(messages.Message):
  team = messages.MessageField(TeamMessage, 1)


class DeleteMembershipRequest(messages.Message):
  team = messages.MessageField(TeamMessage, 1)
  owner = messages.MessageField(owner_messages.OwnerMessage, 2)
  membership = messages.MessageField(TeamMembershipMessage, 3)


class DeleteMembershipResponse(messages.Message):
  team = messages.MessageField(TeamMessage, 1)


class UpdateMembershipRequest(messages.Message):
  team = messages.MessageField(TeamMessage, 1)
  owner = messages.MessageField(owner_messages.OwnerMessage, 2)
  membership = messages.MessageField(TeamMembershipMessage, 3)


class UpdateMembershipResponse(messages.Message):
  team = messages.MessageField(TeamMessage, 1)
