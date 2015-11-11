from ..users import messages as user_messages
from protorpc import messages


class Role(messages.Enum):
  ADMIN = 1
  READ_ONLY = 2
  WRITE = 3
  WRITE_TRANSLATIONS = 4


class Kind(messages.Enum):
  USER = 1
  DOMAIN = 2


class MembershipMessage(messages.Message):
  user = messages.MessageField(user_messages.UserMessage, 1)
  domain = messages.StringField(2)
  role = messages.EnumField(Role, 3)


class GroupMessage(messages.Message):
  users = messages.MessageField(MembershipMessage, 1, repeated=True)
  domains = messages.MessageField(MembershipMessage, 2, repeated=True)
  ident = messages.StringField(3)
