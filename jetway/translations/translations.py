from . import messages


class Translation(object):

  def __init__(self, catalog, msgid, string, comments=None):
    self.catalog = catalog
    self.msgid = msgid or ''
    self.string = string or ''
    self.comments = comments

  @property
  def ident(self):
    return self.catalog.ident + '/' + self.msgid
    if isinstance(self.msgid, unicode):
      msgid = self.msgid.encode('utf-8')
    else:
      msgid = self.msgid
    result = '{}/{}'.format(self.catalog.ident, msgid)
    result = result.decode()
    return result

  def to_message(self):
    message = messages.TranslationMessage()
    message.ident = self.ident
    message.msgid = self.msgid
    message.string = self.string
    return message
