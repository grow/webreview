from protorpc import messages
from ..projects import messages as project_messages


class ActionMessage(messages.Message):
  UNREGISTER = 0
  REGISTER = 1


class BuildMessage(messages.Message):
  project = messages.MessageField(project_messages.ProjectMessage, 1)
  action = messages.EnumField(ActionMessage)
