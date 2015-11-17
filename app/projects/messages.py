from protorpc import messages
from protorpc import message_types
from app.owners import messages as owner_messages


class Permission(messages.Enum):
  READ = 1
  WRITE = 2
  ADMINISTER = 3


class Visibility(messages.Enum):
  PUBLIC = 1
  ORGANIZATION = 2
  PRIVATE = 3
  COVER = 4
  DOMAIN = 5


class Order(messages.Enum):
  NAME = 0


class ProjectMessage(messages.Message):
  nickname = messages.StringField(1)
  ident = messages.StringField(2)
  owner = messages.MessageField(owner_messages.OwnerMessage, 3)
  description = messages.StringField(4)
  avatar_url = messages.StringField(6)
  visibility = messages.EnumField(Visibility, 7)
  name = messages.StringField(9)
  built = message_types.DateTimeField(10)
  buildbot_job_id = messages.StringField(11)
  git_url = messages.StringField(12)


###


class CreateProjectRequest(messages.Message):
  project = messages.MessageField(ProjectMessage, 1)


class CreateProjectResponse(messages.Message):
  project = messages.MessageField(ProjectMessage, 1)


class DeleteProjectRequest(messages.Message):
  project = messages.MessageField(ProjectMessage, 1)


class DeleteProjectResponse(messages.Message):
  pass


class UpdateProjectRequest(messages.Message):
  project = messages.MessageField(ProjectMessage, 1)


class UpdateProjectResponse(messages.Message):
  project = messages.MessageField(ProjectMessage, 1)


class SearchProjectRequest(messages.Message):
  project = messages.MessageField(ProjectMessage, 1)


class SearchProjectResponse(messages.Message):
  projects = messages.MessageField(ProjectMessage, 1, repeated=True)


class GetProjectRequest(messages.Message):
  project = messages.MessageField(ProjectMessage, 1)


class GetProjectResponse(messages.Message):
  project = messages.MessageField(ProjectMessage, 1)


class DeleteProjectRequest(messages.Message):
  project = messages.MessageField(ProjectMessage, 1)


class DeleteProjectResponse(messages.Message):
  pass


class CanRequest(messages.Message):
  project = messages.MessageField(ProjectMessage, 1)
  permission = messages.EnumField(Permission, 2)


class CanResponse(messages.Message):
  can = messages.BooleanField(1)
