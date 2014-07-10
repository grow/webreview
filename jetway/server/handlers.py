from google.appengine.ext import ndb
from jetway.files import files
from jetway.filesets import filesets
from jetway.owners import owners
from jetway.projects import projects
from jetway.server import utils
import jinja2
import os
import webapp2

_path = os.path.join(os.path.dirname(__file__), 'templates')
_loader = jinja2.FileSystemLoader(_path)
_env = jinja2.Environment(loader=_loader, autoescape=True, trim_blocks=True)


class RequestHandler(webapp2.RequestHandler):

  def error(self, status, title, message):
      template = _env.get_template('error.html')
      html = template.render({
        'error': {'title': title, 'message': message},
      })
      self.response.set_status(status)
      self.response.write(html)

  def get(self):
    context = ndb.get_context()
    context.set_cache_policy(lambda key: True)
    context.set_memcache_policy(lambda key: True)
    context.set_memcache_timeout_policy(lambda key: None)
    parts = utils.parse_hostname(os.environ['SERVER_NAME'])
    fileset_name, project_name, owner_name = parts
    try:
      owner = owners.Owner.get(owner_name)
      project = projects.Project.get(owner, project_name)
      if fileset_name is None:
        raise filesets.FilesetDoesNotExistError
      path = (self.request.path + 'index.html'
              if self.request.path.endswith('/') else self.request.path)
      fileset = project.get_fileset(fileset_name)
      headers = fileset.get_headers_for_path(path, request_headers=self.request.headers)
      self.response.headers.update(headers)
    except (owners.OwnerDoesNotExistError,
            projects.ProjectDoesNotExistError,
            filesets.FilesetDoesNotExistError):
#      headers = fileset.get_headers_for_path(
#          self.request.path, request_headers=self.request.headers)
#      self.response.headers.update(headers)
      self.error(404, 'Not Found', 'This fileset does not exist.')
    except files.FileNotFoundError:
      text = 'The URL {} was not found.'
      message = text.format(self.request.path)
      self.error(404, 'Not Found', message)
      return

    if_none_match = self.request.headers.get('If-None-Match')
    if if_none_match and if_none_match == self.response.headers.get('ETag'):
      self.response.status = 304
