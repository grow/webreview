from protorpc import messages


class TranslationMessage(messages.Message):
  msgid = messages.StringField(1)
  string = messages.StringField(2)
