from ..groups import groups
from ..groups import messages
from jetway import api


class Error(Exception):
  pass


class ForbiddenError(Error, api.ForbiddenError):
  pass


class ProjectPolicy(object):

  def __init__(self, user, project):
    self.project = project
    self.user = user

  def authorize_read(self):
    if not self.can_read():
      raise ForbiddenError('{} cannot read {}'.format(self.user, self.project))

  def can_read(self):
    group = self.project.group
    mem = group.get_membership(self.user)
    if mem is None:
      return False
    return mem.role in [messages.Role.ADMIN, messages.Role.READ]

  def can_write(self):
    group = self.project.group
    mem = group.get_membership(self.user)
    if mem is None:
      return False
    return mem.role in [messages.Role.ADMIN, messages.Role.WRITE]
