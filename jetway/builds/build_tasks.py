from google.appengine.ext import ndb
from . import messages

"""
buildbot polls webreview
webreview returns list of projects to register, unregister, and update
buildbot registers and unregisters projects
buildbot updates webreview
"""


class BuildTask(ndb.Model):
  project_key = ndb.KeyProperty()
  action = ndb.MessageProperty(messages.ActionMessage)

  @classmethod
  def create(cls, project, action):
    build_task = cls(project_key=project.key, action=action)
    build_task.put()
    return build_task

  def delete(cls):
    pass

  @classmethod
  def search(cls):
    pass

  def register(cls):
    pass

  def unregister(cls):
    pass

  def to_message(self):
    message = messages.BuildTaskMessage()
    message.project = self.project.to_message()
    message.action = self.action
    return message
