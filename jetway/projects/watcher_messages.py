from . import messages as project_messages
from ..users import messages as user_messages
from protorpc import messages


class WatcherMessage(messages.Message):
  project = messages.MessageField(project_messages.ProjectMessage, 1)
  user = messages.MessageField(user_messages.UserMessage, 2)
  ident = messages.StringField(3)
