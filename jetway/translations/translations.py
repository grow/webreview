from . import messages


class Translation(object):

  def __init__(self, catalog, msgid, string):
    self.catalog = catalog
    self.msgid = msgid
    self.string = string

  def to_message(self):
    message = messages.TranslationMessage()
    message.msgid = self.msgid
    message.string = self.string
    return message
