from google.appengine.ext import blobstore
from app.avatars import avatars
from app.users import users
from app.auth import handlers as auth_handlers
import appengine_config
import jinja2
import os
import webapp2

_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), '..', '..', 'dist'))
_loader = jinja2.FileSystemLoader(_path)
_env = jinja2.Environment(loader=_loader, autoescape=True, trim_blocks=True)


class BaseHandler(auth_handlers.SessionHandler):

  def respond(self, template_name, params=None):
    template = _env.get_template(template_name)
    params = params or {}
    params.update({
        'me': self.me,
        'config': appengine_config.jetway_config,
        'version': os.getenv('CURRENT_VERSION_ID', 'xxx'),
    })
    if self.me is None:
      params['sign_in_url'] = self.create_sign_in_url()
    else:
      params['sign_out_url'] = self.create_sign_out_url()
    self.response.write(template.render(params))


class FrontendHandler(BaseHandler):

  def get(self):
    self.respond('index.html')


class AvatarHandler(webapp2.RequestHandler):

  def error(self, status=404):
    self.response.set_status(status)

  def get(self, letter, ident):
    status, headers, content = users.User.get_response_for_avatar(
        self.request.headers, letter, ident)
    self.response.status = status
    self.response.headers.update(headers)
    if content:
      self.response.out.write(content)

  def post(self, letter, ident):
    cgi_data = self.request.POST['file']
    file_info = blobstore.parse_file_info(cgi_data)
    gs_object_name = file_info.gs_object_name
    try:
      avatar = avatars.Avatar.get(letter, ident)
      avatar.update(gs_object_name)
    except avatars.AvatarDoesNotExistError:
      avatar = avatars.Avatar.create(letter, ident, gs_object_name)
