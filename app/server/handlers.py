from google.appengine.ext import ndb
from app.auth import handlers as auth_handlers
from app.files import files
from app.filesets import filesets
from app.owners import owners
from app.policies import policies
from app.projects import projects
from app.server import utils
import jinja2
import os

_path = os.path.join(os.path.dirname(__file__), 'templates')
_loader = jinja2.FileSystemLoader(_path)
_env = jinja2.Environment(loader=_loader, autoescape=True, trim_blocks=True)


class RequestHandler(auth_handlers.SessionHandler):

  def _is_open_path(self, path):
    # TODO: Remove dirty hack to get around issues with Chrome Beta and
    # Firefox. Note that this exposes all ttf and woff files.
    # http://stackoverflow.com/questions/31140826
    return path.endswith(('.woff', '.ttf'))

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
    parts = utils.parse_hostname(os.environ['SERVER_NAME'], multitenant=False)
    try:
      # On the root-level preview domain, where there is never a fileset.
      if parts is None:
        raise filesets.FilesetDoesNotExistError()
      if len(parts) == 3:
        fileset_name, project_name, owner_name = parts
        owner = owners.Owner.get(owner_name)
        project = projects.Project.get(owner, project_name)
        if fileset_name is None:
          raise filesets.FilesetDoesNotExistError
        fileset = project.get_fileset(fileset_name)
      else:
        fileset_name = parts[0]
        if fileset_name is None:
          raise filesets.FilesetDoesNotExistError
        fileset = filesets.Fileset.get_by_name_or_ident(fileset_name)
      policy = policies.ProjectPolicy(self.me, fileset.project)
      if not self._is_open_path(self.request.path) and not policy.can_read():
        if self.me:
          text = '{} does not have access to this page.'.format(self.me)
          self.error(403, 'Forbidden', text)
          return
        else:
          text = 'You must be signed in to view this page.'
          self.error(404, 'Not Found', text)
          return
      path = (self.request.path + 'index.html'
              if self.request.path.endswith('/') else self.request.path)
      headers = fileset.get_headers_for_path(
          path, request_headers=self.request.headers)
      self.response.headers.update(headers)

    except (owners.OwnerDoesNotExistError,
            projects.ProjectDoesNotExistError,
            filesets.FilesetDoesNotExistError):
      self.error(404, 'Not Found', 'This fileset does not exist.')

    except files.FileNotFoundError:
      text = 'The URL {} was not found.'
      message = text.format(self.request.path)
      self.error(404, 'Not Found', message)
      return
    if_none_match = self.request.headers.get('If-None-Match')
    if if_none_match and if_none_match == self.response.headers.get('ETag'):
      self.response.status = 304
    if 'X-WebReview-Redirect-Status' in self.response.headers:
      status = self.response.headers['X-WebReview-Redirect-Status']
      self.response.status = int(status)