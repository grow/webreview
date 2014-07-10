from protorpc import messages
from protorpc import message_types


class OrgMessage(messages.Message):
  nickname = messages.StringField(1)
  avatar_url = messages.StringField(2)
  description = messages.StringField(3)
  location = messages.StringField(4)
  created = message_types.DateTimeField(5)
  updated = message_types.DateTimeField(6)
  avatar_url = messages.StringField(7)
  ident = messages.StringField(8)
