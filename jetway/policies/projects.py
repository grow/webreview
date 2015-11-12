from ..groups import groups
from ..groups import messages
from jetway import api_errors


class Error(Exception):
  pass


class ForbiddenError(Error, api_errors.ForbiddenError):
  pass


class ProjectPolicy(object):

  def __init__(self, user, project):
    self.project = project
    self.user = user
    self.mem = self.project.group.get_membership(self.user)
    self.is_owner = self.project.owner_key == user.key

  def authorize_admin(self):
    if not self.can_write():
      raise ForbiddenError('{} is not an admin for {}'.format(self.user, self.project))

  def authorize_write(self):
    if not self.can_write():
      raise ForbiddenError('{} cannot write to {}'.format(self.user, self.project))

  def authorize_read(self):
    if not self.can_read():
      raise ForbiddenError('{} cannot read {}'.format(self.user, self.project))

  def can_administer(self):
    if self.is_owner:
      return True
    if self.mem is None:
      return False
    return self.mem.role in [messages.Role.ADMIN]

  def can_read(self):
    if self.is_owner:
      return True
    if self.mem is None:
      return False
    return self.mem.role in [messages.Role.ADMIN, messages.Role.READ, None]

  def can_write(self):
    if self.is_owner:
      return True
    if self.mem is None:
      return False
    return self.mem.role in [messages.Role.ADMIN, messages.Role.WRITE]
