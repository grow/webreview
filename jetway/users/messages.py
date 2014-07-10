from protorpc import messages
from jetway.orgs import messages as org_messages
from jetway.projects import messages as project_messages


class UserMessage(messages.Message):
  ident = messages.StringField(1)
  nickname = messages.StringField(2)
  avatar_url = messages.StringField(3)
  email = messages.StringField(4)
  website_url = messages.StringField(5)
  description = messages.StringField(6)
  location = messages.StringField(7)


###


class GetMeRequest(messages.Message):
  pass


class GetMeResponse(messages.Message):
  me = messages.MessageField(UserMessage, 1)


class RegenerateGitPasswordRequest(messages.Message):
  pass


class RegenerateGitPasswordResponse(messages.Message):
  me = messages.MessageField(UserMessage, 1)
  git_password = messages.StringField(2)


class SignInRequest(messages.Message):
  pass


class SignInResponse(messages.Message):
  me = messages.MessageField(UserMessage, 1)


class SignOutRequest(messages.Message):
  pass


class SignOutResponse(messages.Message):
  pass


class UpdateMeRequest(messages.Message):
  me = messages.MessageField(UserMessage, 1)


class UpdateMeResponse(messages.Message):
  me = messages.MessageField(UserMessage, 1)


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
