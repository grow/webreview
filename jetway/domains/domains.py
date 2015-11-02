from jetway import models
from google.appengine.ext import ndb


class Domain(models.Model):
  name = ndb.StringProperty()
