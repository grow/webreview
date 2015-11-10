from ..buildbot import messages as buildbot_messages
from ..catalogs import messages as catalog_messages
from ..filesets.named_fileset_messages import *
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
  watching = messages.BooleanField(2)


class CreateWatcherResponse(messages.Message):
  watcher = messages.MessageField(WatcherMessage, 1)


class ListNamedFilesetsRequest(messages.Message):
  project = messages.MessageField(ProjectMessage, 1)


class ListNamedFilesetsResponse(messages.Message):
  named_filesets = messages.MessageField(NamedFilesetMessage, 1, repeated=True)


class CreateNamedFilesetRequest(messages.Message):
  project = messages.MessageField(ProjectMessage, 1)
  named_fileset = messages.MessageField(NamedFilesetMessage, 2)


class CreateNamedFilesetResponse(messages.Message):
  named_fileset = messages.MessageField(NamedFilesetMessage, 1)


class DeleteNamedFilesetRequest(messages.Message):
  project = messages.MessageField(ProjectMessage, 1)
  named_fileset = messages.MessageField(NamedFilesetMessage, 2)


class DeleteNamedFilesetResponse(messages.Message):
  named_fileset = messages.MessageField(NamedFilesetMessage, 1)


class ListBranchesRequest(messages.Message):
  project = messages.MessageField(ProjectMessage, 1)


class ListBranchesResponse(messages.Message):
  branches = messages.MessageField(buildbot_messages.BranchMessage, 1, repeated=True)


class ProjectRequest(messages.Message):
  project = messages.MessageField(ProjectMessage, 1)


class ListCatalogsResponse(messages.Message):
  catalogs = messages.MessageField(catalog_messages.CatalogMessage, 1, repeated=True)


class CatalogRequest(messages.Message):
  project = messages.MessageField(ProjectMessage, 1)
  catalog = messages.MessageField(catalog_messages.CatalogMessage, 2)


class CatalogResponse(messages.Message):
  catalog = messages.MessageField(catalog_messages.CatalogMessage, 1)
