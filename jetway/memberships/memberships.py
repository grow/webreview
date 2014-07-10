from google.appengine.ext import ndb


class Error(Exception):
  pass


class MembershipExistsError(Error):
  pass


class MembershipDoesNotExistError(Error):
  pass


class Membership(ndb.Model):
  parent_key = ndb.KeyProperty()
  user_key = ndb.KeyProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)
  updated = ndb.DateTimeProperty(auto_now=True)
  # role

  @classmethod
  def create(cls, parent, user, role):
    try:
      cls.get(parent, user)
      text = '{} is already a member of {}.'
      raise MembershipExistsError(text.format(user, parent))
    except MembershipDoesNotExistError:
      membership = cls(
          parent_key=parent.key,
          user_key=user.key,
          role=role,
          parent=parent.key)
      membership.put()
      return membership

  @classmethod
  def get(cls, parent, user):
    query = cls.query(ancestor=parent.key)
    query = query.filter(cls.user_key == user.key)
    results = query.fetch(1)
    membership = results[0] if len(results) else None
    if membership is None:
      text = '"{}" is not a member of "{}"'
      raise MembershipDoesNotExistError(text.format(user, parent))
    return membership

  @classmethod
  def list(cls, parent=None, user=None):
    query = cls.query() if parent is None else cls.query(ancestor=parent.key)
    if user is not None:
      query = query.filter(cls.user_key == user.key)
    return query.fetch()

  def delete(self):
    self.key.delete()

  @property
  def user(self):
    return self.user_key.get()

  @property
  def ident(self):
    return self.key.integer_id()
