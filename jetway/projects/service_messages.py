from .messages import *
from .watcher_messages import *
from protorpc import messages


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


class ListWatchersRequest(messages.Message):
  project = messages.MessageField(ProjectMessage, 1)


class ListWatchersResponse(messages.Message):
  watchers = messages.MessageField(WatcherMessage, 1, repeated=True)
