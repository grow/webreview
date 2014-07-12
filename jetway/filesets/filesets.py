from google.appengine.ext import ndb
from jetway.files import files
from jetway.files import messages as file_messages
from jetway.filesets import messages
from jetway.server import utils
from jetway.logs import logs
import appengine_config
import os
import webapp2


class Error(Exception):
  pass


class FilesetExistsError(Error):
  pass


class FilesetDoesNotExistError(Error):
  pass


class FileCount(ndb.Model):
  ext = ndb.StringProperty()
  count = ndb.IntegerProperty()

  @classmethod
  def from_message(cls, message):
    return cls(ext=message.ext, count=message.count)

  def to_message(self):
    message = messages.FileCountMessage()
    message.ext = self.ext
    message.count = self.count
    return message


class Resource(ndb.Model):
  path = ndb.StringProperty()
  locale = ndb.StringProperty()
  sha = ndb.StringProperty()

  @classmethod
  def from_message(cls, message):
    return cls(path=message.path,
               locale=message.locale,
               sha=message.sha)

  def to_message(self):
    message = messages.ResourceMessage()
    message.path = self.path
    message.sha = self.sha
    message.locale = self.locale
    return message


class File(ndb.Model):
  path = ndb.StringProperty()
  created_by = ndb.StringProperty()
  modified_by = ndb.StringProperty()
  size = ndb.IntegerProperty()
  ext = ndb.ComputedProperty(lambda self: os.path.splitext(self.path)[-1])
  sha = ndb.StringProperty()

  def to_message(self):
    message = messages.FileMessage()
    message.path = self.apth
    message.created_by = self.created_by
    message.modified_by = self.modified_by
    message.ext = self.ext
    message.size = self.size
    return message


class FilesetStats(ndb.Model):
  num_collections = ndb.IntegerProperty()
  num_documents = ndb.IntegerProperty()
  num_static_files = ndb.IntegerProperty()
  num_files_per_type = ndb.StructuredProperty(FileCount, repeated=True)
  locales = ndb.StringProperty(repeated=True)
  num_messages = ndb.IntegerProperty()
  num_untranslated_messages = ndb.IntegerProperty()

  @classmethod
  def from_message(cls, message):
    return cls(
        num_collections=message.num_collections,
        num_documents=message.num_documents,
        num_static_files=message.num_static_files,
        num_files_per_type=[FileCount.from_message(n)
                            for n in message.num_files_per_type],
        locales=message.locales,
        num_messages=message.num_messages,
        num_untranslated_messages=message.num_untranslated_messages)

  def to_message(self):
    message = messages.StatsMessage()
    message.num_collections = self.num_collections
    message.num_documents = self.num_documents
    message.num_static_files = self.num_static_files
    message.num_files_per_type = [f.to_message()
                                  for f in self.num_files_per_type]
    message.locales = self.locales
    message.num_messages = self.num_messages
    message.num_untranslated_messages = self.num_untranslated_messages
    return message


class Fileset(ndb.Model):
  name = ndb.StringProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)
  created_by_key = ndb.KeyProperty()
  project_key = ndb.KeyProperty()
  modified = ndb.DateTimeProperty(auto_now=True)
  modified_by_key = ndb.KeyProperty()
  log = ndb.StructuredProperty(logs.Log)
  stats = ndb.StructuredProperty(FilesetStats)
  resources = ndb.StructuredProperty(Resource, repeated=True)
  source_files = ndb.StructuredProperty(File, repeated=True)

  @classmethod
  def create(cls, project, name, created_by=None):
    try:
      cls.get(name=name)
      raise FilesetExistsError('Fileset "{}" already exists.'.format(name))
    except FilesetDoesNotExistError:
      pass
    fileset = cls(project_key=project.key, name=name)
    if created_by:
      fileset.created_by_key = created_by.key
    fileset.put()
    return fileset

  @classmethod
  def get_by_ident(cls, ident):
    key = ndb.Key('Fileset', int(ident))
    fileset = key.get()
    if fileset is None:
      raise FilesetDoesNotExistError('Fileset "{}" does not exist.'.format(ident))
    return fileset

  @classmethod
  def get(cls, project=None, name=None):
    query = cls.query()
    if project is not None:
      query = query.filter(cls.project_key == project.key)
    if name is not None:
      query = query.filter(cls.name == name)
    fileset = query.get()
    if fileset is None:
      text = 'Fileset "{}" does not exist.'
      raise FilesetDoesNotExistError(text.format(name))
    return fileset

  def __repr__(self):
    return '<Filset: {}/{}@{} ({})>'.format(
        self.project.owner.nickname, self.project.nickname, self.name,
        self.ident)

  @property
  def ident(self):
    return str(self.key.id())

  @webapp2.cached_property
  def project(self):
    return self.project_key.get()

  @property
  def created_by(self):
    return self.created_by_key.get()

  @classmethod
  def search(cls, project=None):
    query = cls.query()
    if project:
      query = query.filter(cls.project_key == project.key)
    return query.fetch()

  def delete(self):
    self.key.delete()

  def update(self, message):
    if message.log:
      self.log = logs.Log.from_message(message.log)
    if message.stats:
      self.stats = FilesetStats.from_message(message.stats)
    if message.resources:
      self.resources = [Resource.from_message(message)
                        for message in message.resources]
    self.put()

  def to_message(self):
    message = messages.FilesetMessage()
    message.name = self.name
    message.ident = self.ident
    message.url = self.url
    message.modified = self.modified
    if self.created_by_key:
      message.created_by = self.created_by.to_message()
    if self.log:
      message.log = self.log.to_message()
    if self.stats:
      message.stats = self.stats.to_message()
    if self.resources:
      message.resources = [resource.to_message() for resource in self.resources]
    return message

  @property
  def url(self):
    return utils.make_url(self.name, self.project.nickname,
                          self.project.owner.nickname)

  @webapp2.cached_property
  def _signer(self):
    gcs_bucket = appengine_config.jetway_config['app']['gcs_bucket']
    root = '/{}/jetway/filesets/{}'.format(gcs_bucket, self.ident)
    return files.Signer(root)

  def sign_requests(self, unsigned_requests):
    signed_reqs = []
    for req in unsigned_requests:
      if req.verb == file_messages.Verb.PUT:
        signed_reqs.append(self.sign_put_request(req))
      elif req.verb == file_messages.Verb.DELETE:
        signed_reqs.append(self.sign_delete_request(req))
      elif req.verb == file_messages.Verb.GET:
        signed_reqs.append(self.sign_get_request(req))
    return signed_reqs

  def sign_put_request(self, unsigned_request):
    return self._signer.sign_put_request(unsigned_request)

  def sign_delete_request(self, unsigned_request):
    return self._signer.sign_delete_request(unsigned_request)

  def sign_get_request(self, unsigned_request):
    return self._signer.sign_get_request(unsigned_request)

  def get_headers_for_path(self, path, request_headers=None):
    return self._signer.get_headers_for_path(path, request_headers=request_headers)

  def get_sha_for_resource_path(self, path):
    for resource in self.resources:
      if path == resource.path:
        return resource.sha
    raise ValueError('Resource with path {} not found.'.format(path))
