from protorpc import messages
from protorpc import message_types
from ..translations import messages as translation_messages


class CatalogMessage(messages.Message):
  locale = messages.StringField(1)
  translations = messages.MessageField(
      translation_messages.TranslationMessage, 2, repeated=True)
  name = messages.StringField(3)
  percent_translated = messages.IntegerField(4)
  modified = message_types.DateTimeField(5)
  num_fuzzy = messages.IntegerField(6)
  num_translated = messages.IntegerField(7)
  num_messages = messages.IntegerField(8)
  ident = messages.StringField(9)
  sha = messages.StringField(10)
  ref = messages.StringField(11)
