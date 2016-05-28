from .messages import UserMessage
from app.orgs import messages as org_messages
from app.projects import messages as project_messages
from protorpc import messages


class GetMeRequest(messages.Message):
  pass


class GetMeResponse(messages.Message):
  me = messages.MessageField(UserMessage, 1)  # TODO: Deprecate "me".
  user = messages.MessageField(UserMessage, 2)


class SignInRequest(messages.Message):
  pass


class SignInResponse(messages.Message):
  me = messages.MessageField(UserMessage, 1)


class SignOutRequest(messages.Message):
  pass


class SignOutResponse(messages.Message):
  pass


class UpdateMeRequest(messages.Message):
  me = messages.MessageField(UserMessage, 1)  # TODO: Deprecate "me".
  user = messages.MessageField(UserMessage, 2)


class UpdateMeResponse(messages.Message):
  me = messages.MessageField(UserMessage, 1)  # TODO: Deprecate "me".
  user = messages.MessageField(UserMessage, 2)


class SearchOrgsRequest(messages.Message):
  user = messages.MessageField(UserMessage, 1)


class SearchOrgsResponse(messages.Message):
  orgs = messages.MessageField(org_messages.OrgMessage, 1, repeated=True)


class SearchProjectsRequest(messages.Message):
  user = messages.MessageField(UserMessage, 1)


class SearchProjectsResponse(messages.Message):
  projects = messages.MessageField(project_messages.ProjectMessage, 1, repeated=True)


class SearchRequest(messages.Message):
  project = messages.MessageField(project_messages.ProjectMessage, 1)


class SearchResponse(messages.Message):
  users = messages.MessageField(UserMessage, 1, repeated=True)
