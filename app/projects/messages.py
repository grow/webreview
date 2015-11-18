from protorpc import messages
from protorpc import message_types
from app.owners import messages as owner_messages


class Permission(messages.Enum):
  READ = 1
  WRITE = 2
  ADMINISTER = 3


class Order(messages.Enum):
  NAME = 0


class BuildbotGitStatus(messages.Enum):
  NONE = 1
  SYNCING = 2
  ERROR = 3
  CONNECTED = 4


class ProjectMessage(messages.Message):
  nickname = messages.StringField(1)
  ident = messages.StringField(2)
  owner = messages.MessageField(owner_messages.OwnerMessage, 3)
  description = messages.StringField(4)
  avatar_url = messages.StringField(6)
  name = messages.StringField(9)
  built = message_types.DateTimeField(10)
  buildbot_job_id = messages.StringField(11)
  git_url = messages.StringField(12)
  translation_branch = messages.StringField(13)
  buildbot_git_status = messages.EnumField(BuildbotGitStatus, 14)


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
