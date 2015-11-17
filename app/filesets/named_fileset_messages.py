from protorpc import messages


class NamedFilesetMessage(messages.Message):
  ident = messages.StringField(1)
  branch = messages.StringField(2)
