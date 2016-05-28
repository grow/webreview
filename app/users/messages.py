from protorpc import messages


class UserMessage(messages.Message):
  ident = messages.StringField(1)
  nickname = messages.StringField(2)
  avatar_url = messages.StringField(3)
  email = messages.StringField(4)
  website_url = messages.StringField(5)
  description = messages.StringField(6)
  location = messages.StringField(7)
  name = messages.StringField(8)
