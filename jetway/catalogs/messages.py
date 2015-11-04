from protorpc import messages


class CatalogMessage(messages.Message):
  locale = messages.StringField(1)
