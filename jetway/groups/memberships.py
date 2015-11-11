from . import messages
from ..users import users
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop
import webapp2


class Error(Exception):
  pass


class MembershipConflictError(Error):
  pass


class Membership(ndb.Model):
  user_key = ndb.KeyProperty()
  domain = ndb.StringProperty()
  role = msgprop.EnumProperty(messages.Role)

  def check_conflict(self, other_memberships):
    for mem in other_memberships:
      if self.user_key and self.user_key == mem.user_key:
        raise MembershipConflictError()
      if self.domain and self.domain == mem.domain:
        raise MembershipConflictError()

  @classmethod
  def from_message(cls, message):
    mem = cls()
    mem.role = message.role
    if message.user:
      user = users.User.get_by_ident(message.user.ident)
      mem.user_key = user.key
    if message.domain:
      mem.domain = message.domain
    return mem

  @webapp2.cached_property
  def user(self):
    if self.user_key:
      return self.user_key.get()

  def to_message(self):
    message = messages.MembershipMessage()
    if self.user_key:
      message.user = self.user.to_message()
    if self.domain:
      message.domain = self.domain
    return message