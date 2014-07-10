from google.appengine.ext import ndb
from jetway.logs import messages
from jetway.users import users


class LogAuthor(ndb.Model):
  name = ndb.StringProperty()
  email = ndb.StringProperty()
  user_key = ndb.KeyProperty()

  def __hash__(self):
    return hash((self.email, self.user_key))

  def __eq__(self, other):
    return (isinstance(self, type(other))
            and self.email == other.email
            and self.user_key == other.user_key)

  @classmethod
  def from_message(cls, message):
    user = users.User.get_by_email(message.email)
    log_author = cls(name=message.name, email=message.email)
    if user:
      log_author.user_key = user.key
    return log_author

  @property
  def user(self):
    if self.user_key:
      return self.user_key.get()

  def to_message(self):
    message = messages.AuthorMessage()
    message.name = self.name
    message.email = self.email
    if self.user:
      message.user = self.user.to_message()
    return message


class LogItem(ndb.Model):
  author = ndb.StructuredProperty(LogAuthor)
  commit = ndb.StringProperty()
  date = ndb.DateTimeProperty()
  message = ndb.StringProperty()

  @classmethod
  def from_message(cls, message):
    return cls(author=LogAuthor.from_message(message.author),
               commit=message.commit,
               date=message.date,
               message=message.message)

  def to_message(self):
    message = messages.LogItemMessage()
    if self.author:
      message.author = self.author.to_message()
    message.date = self.date
    message.message = self.message
    return message


class Log(ndb.Model):
  items = ndb.StructuredProperty(LogItem, repeated=True)

  @classmethod
  def from_message(cls, message):
    items = [LogItem.from_message(item) for item in message.items]
    return cls(items=items)

  @classmethod
  def get_user_keys_from_items(cls, items):
    emails = list(set(item.author.email for item in items))
    ents = users.User.get_multi_by_email(emails)
    return [ent.key for ent in ents]

  def search_authors(self):
    return set([item.author for item in self.items])

  def to_message(self):
    message = messages.LogMessage()
    message.items = [item.to_message() for item in self.items]
    message.authors = [author.to_message() for author in self.search_authors()]
    return message
