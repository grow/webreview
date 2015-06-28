from protorpc import messages
from jetway.owners import messages as owner_messages


class Permission(messages.Enum):
  READ = 1
  WRITE = 2
  ADMINISTER = 3


class Visibility(messages.Enum):
  PUBLIC = 1
  ORGANIZATION = 2
  PRIVATE = 3
  COVER = 4


class CoverMessage(messages.Message):
  content = messages.StringField(1)


class Order(messages.Enum):
  NAME = 0


class ProjectMessage(messages.Message):
  nickname = messages.StringField(1)
  ident = messages.StringField(2)
  owner = messages.MessageField(owner_messages.OwnerMessage, 3)
  description = messages.StringField(4)
  git_url = messages.StringField(5)
  avatar_url = messages.StringField(6)
  visibility = messages.EnumField(Visibility, 7)
  cover = messages.MessageField(CoverMessage, 8)
  name = messages.StringField(9)


