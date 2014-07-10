from protorpc import messages
from protorpc import message_types
from jetway.users import messages as user_messages


class AuthorMessage(messages.Message):
  name = messages.StringField(1)
  email = messages.StringField(2)
  user = messages.MessageField(user_messages.UserMessage, 3)


class LogItemMessage(messages.Message):
  author = messages.MessageField(AuthorMessage, 1)
  date = message_types.DateTimeField(2)
  message = messages.StringField(3)
  commit = messages.StringField(4)


class LogMessage(messages.Message):
  items = messages.MessageField(LogItemMessage, 1, repeated=True)
  authors = messages.MessageField(AuthorMessage, 2, repeated=True)
