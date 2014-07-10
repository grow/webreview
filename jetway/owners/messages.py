from protorpc import messages
from protorpc import message_types


class OwnerMessage(messages.Message):

  class Kind(messages.Enum):
    USER = 1
    ORG = 2

  nickname = messages.StringField(1)
  ident = messages.StringField(2)
  description = messages.StringField(3)
  location = messages.StringField(4)
  website_url = messages.StringField(5)
  created = message_types.DateTimeField(6)
  avatar_url = messages.StringField(7)
  kind = messages.EnumField(Kind, 8)
  email = messages.StringField(9)


###


class CreateOwnerRequest(messages.Message):
  owner = messages.MessageField(OwnerMessage, 1)


class CreateOwnerResponse(messages.Message):
  owner = messages.MessageField(OwnerMessage, 1)


class DeleteOwnerRequest(messages.Message):
  owner = messages.MessageField(OwnerMessage, 1)


class DeleteOwnerResponse(messages.Message):
  pass


class UpdateOwnerRequest(messages.Message):
  owner = messages.MessageField(OwnerMessage, 1)


class UpdateOwnerResponse(messages.Message):
  owner = messages.MessageField(OwnerMessage, 1)


class SearchOwnerRequest(messages.Message):
  pass


class SearchOwnerResponse(messages.Message):
  owners = messages.MessageField(OwnerMessage, 1, repeated=True)


class GetOwnerRequest(messages.Message):
  owner = messages.MessageField(OwnerMessage, 1)


class GetOwnerResponse(messages.Message):
  owner = messages.MessageField(OwnerMessage, 1)


class SearchProjectRequest(messages.Message):
  owner = messages.MessageField(OwnerMessage, 1)


class SearchProjectResponse(messages.Message):
  owner = messages.MessageField(OwnerMessage, 1)
