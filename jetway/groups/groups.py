from . import messages
from . import memberships
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop


class Error(Exception):
  pass


class Group(ndb.Model):
  memberships = ndb.StructuredProperty(repeated=True)

  @property
  def ident(self):
    return self.key.urlsafe()

  @classmethod
  def get(cls, ident):
    key = ndb.Key(urlsafe=ident)
    group = key.get()
    if group is None:
      raise Error('Group does not exist.')
    return group

  def validate(self):
    num_admins = 0
    for mem in self.memberships:
      if mem.role == messages.Role.ADMIN:
        num_admins += 1
    if num_admins < 1:
      raise memberships.MembershipConflictError('Must be at least one admin.')

  def create_membership(self, membership_message):
    mem = memberships.Membership.from_message(membership_message)
    mem.check_conflict(self.memberships)
    self.memberships.append(mem)
    self.validate()
    self.put()
    return self

  def delete_membership(self, membership_message):
    mem = memberships.Membership.from_message(membership_message)
    for i, each_mem in enumerate(self.memberships):
      if each_mem == mem:
        del self.memberships[i]
        self.validate()
        self.put()
        return self
    raise memberships.MembershipConflictError('Membership does not exist.')

  def list_memberships(self, kind=None):
    mems = []
    for mem in self.memberships:
      if kind is None:
        mems.append(mem)
      elif kind == messages.Kind.USER and mem.user_key:
        mems.append(mem)
      elif kind == messages.Kind.DOMAIN and mem.domain:
        mems.append(mem)
    return mems

  def to_message(self):
    message = messages.GroupMessage()
    message.ident = self.ident
    message.users = [mem.to_message()
                     for mem in self.list_memberships(messages.Kind.USER)]
    message.domains = [mem.to_message()
                       for mem in self.list_memberships(messages.Kind.DOMAIN)]
    return message
