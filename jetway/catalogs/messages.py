from protorpc import messages
from ..translations import messages as translation_messages


class CatalogMessage(messages.Message):
  locale = messages.StringField(1)
  translations = messages.MessageField(translation_messages.TranslationMessage, 2, repeated=True)
