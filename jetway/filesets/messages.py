from jetway.files import messages as file_messages
from jetway.projects import messages as project_messages
from jetway.users import messages as user_messages
from protorpc import message_types
from protorpc import messages


class AuthorMessage(messages.Message):
  name = messages.StringField(1)
  email = messages.StringField(2)


class CommitMessage(messages.Message):
  sha = messages.StringField(1)
  author = messages.MessageField(AuthorMessage, 2)
  date = message_types.DateTimeField(3)
  message = messages.StringField(4)
  has_unstaged_changes = messages.BooleanField(5)
  branch = messages.StringField(6)


class FileCountMessage(messages.Message):
  ext = messages.StringField(1)
  count = messages.IntegerField(2)


class ResourceMessage(messages.Message):
  path = messages.StringField(1)
  locale = messages.StringField(2)
  sha = messages.StringField(3)


class FilesetStatus(messages.Enum):
  BUILDING = 0
  SUCCESS = 1
  BROKEN = 2


class FileMessage(messages.Message):
  path = messages.StringField(1)
  created_by = messages.StringField(2)
  modified_by = messages.StringField(3)
  ext = messages.StringField(4)
  size = messages.IntegerField(5)
  sha = messages.StringField(6)


class StatsMessage(messages.Message):
  num_collections = messages.IntegerField(101)
  num_documents = messages.IntegerField(102)
  num_static_files = messages.IntegerField(103)
  num_files_per_type = messages.MessageField(FileCountMessage, 104, repeated=True)

  locales = messages.StringField(123, repeated=True)
  langs = messages.StringField(124, repeated=True)
  num_messages = messages.IntegerField(125)
  num_untranslated_messages = messages.IntegerField(126)


class PageSpeedStatsMessage(messages.Message):
  name = messages.StringField(1)
  value = messages.StringField(2)


class PageSpeedArgMessage(messages.Message):
  type = messages.StringField(1)
  value = messages.StringField(2)


class PageSpeedUrlResultMessage(messages.Message):
  format = messages.StringField(1)
  args = messages.MessageField(PageSpeedArgMessage, 2, repeated=True)


class PageSpeedRuleMessage(messages.Message):
  name = messages.StringField(1)
  impact = messages.IntegerField(2)
  header = messages.MessageField(PageSpeedUrlResultMessage, 3, repeated=True)
  urls = messages.MessageField(PageSpeedUrlResultMessage, 4, repeated=True)


class PageSpeedResultMessage(messages.Message):
  page_stats = messages.MessageField(PageSpeedStatsMessage, 1, repeated=True)
  response_code = messages.IntegerField(2)
  page_rules = messages.MessageField(PageSpeedRuleMessage, 3, repeated=True)


class FilesetMessage(messages.Message):
  ident = messages.StringField(1)
  unsigned_requests = messages.MessageField(file_messages.UnsignedRequest, 2, repeated=True)
  signed_requests = messages.MessageField(file_messages.SignedRequest, 3, repeated=True)
  name = messages.StringField(4)
  project = messages.MessageField(project_messages.ProjectMessage, 5)
  url = messages.StringField(6)
  modified = message_types.DateTimeField(7)
  message = messages.StringField(9)
  stats = messages.MessageField(StatsMessage, 10)
  resources = messages.MessageField(ResourceMessage, 11, repeated=True)
  files = messages.MessageField(FileMessage, 12, repeated=True)
  created_by = messages.MessageField(user_messages.UserMessage, 13)
  commit = messages.MessageField(CommitMessage, 14)
  finalized = messages.BooleanField(15)
  status = messages.EnumField(FilesetStatus, 16)


class NamedFilesetMessage(messages.Message):
  ident = messages.StringField(1)
  name = messages.StringField(2)
  branch = messages.StringField(3)
  project = messages.MessageField(project_messages.ProjectMessage, 4)
  created = message_types.DateTimeField(5)


###


class CreateFilesetRequest(messages.Message):
  fileset = messages.MessageField(FilesetMessage, 1)


class CreateFilesetResponse(messages.Message):
  fileset = messages.MessageField(FilesetMessage, 1)


class DeleteFilesetRequest(messages.Message):
  fileset = messages.MessageField(FilesetMessage, 1)


class DeleteFilesetResponse(messages.Message):
  fileset = messages.MessageField(FilesetMessage, 1)


class SearchFilesetRequest(messages.Message):
  fileset = messages.MessageField(FilesetMessage, 1)


class SearchFilesetResponse(messages.Message):
  filesets = messages.MessageField(FilesetMessage, 1, repeated=True)


class GetFilesetRequest(messages.Message):
  fileset = messages.MessageField(FilesetMessage, 1)


class GetFilesetResponse(messages.Message):
  fileset = messages.MessageField(FilesetMessage, 1)


class SignRequestsRequest(messages.Message):
  fileset = messages.MessageField(FilesetMessage, 1)
  unsigned_requests = messages.MessageField(file_messages.UnsignedRequest, 2, repeated=True)


class SignRequestsResponse(messages.Message):
  fileset = messages.MessageField(FilesetMessage, 1)
  signed_requests = messages.MessageField(file_messages.SignedRequest, 2, repeated=True)


class FinalizeRequest(messages.Message):
  fileset = messages.MessageField(FilesetMessage, 1)


class FinalizeResponse(messages.Message):
  fileset = messages.MessageField(FilesetMessage, 1)


class GetPageSpeedResultRequest(messages.Message):
  fileset = messages.MessageField(FilesetMessage, 1)
  file = messages.MessageField(file_messages.FileMessage, 2)


class GetPageSpeedResultResponse(messages.Message):
  pagespeed_result = messages.MessageField(PageSpeedResultMessage, 1)
