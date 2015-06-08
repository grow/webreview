from google.appengine.ext import ndb


class Memory(ndb.Model):
  name = ndb.StringProperty()
