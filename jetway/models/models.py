from google.appengine.ext import ndb


class Model(ndb.Model):
  _message_class = None

  @classmethod
  def create(cls, message):
    pass

  @classmethod
  def get_or_create(cls, name):
    pass

  @classmethod
  def get(cls, name):
    pass
