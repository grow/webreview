import appengine_config
from google.appengine.api import users
from .auth import handlers as auth_handlers
from .avatars import services as avatar_services
from .comments import services as comment_services
from .filesets import services as fileset_services
from .frontend import handlers as frontend_handlers
from .launches import services as launch_services
from .orgs import services as org_services
from .owners import services as owner_services
from .projects import services as project_services
from .server import handlers as server_handlers
from .server import utils
from .teams import services as team_services
from .users import services as user_services
from protorpc.wsgi import service
import webapp2


frontend_app = webapp2.WSGIApplication([
    ('/avatars/(u|o|p)/(.*)', frontend_handlers.AvatarHandler),
    ('/me/signout', auth_handlers.SignOutHandler),
    ('/[^/]*/[^/]*.git.*', frontend_handlers.GitRedirectHandler),
    ('.*', frontend_handlers.FrontendHandler),
], config=appengine_config.WEBAPP2_AUTH_CONFIG)

server_app = webapp2.WSGIApplication([
    ('.*', server_handlers.RequestHandler),
], config=appengine_config.WEBAPP2_AUTH_CONFIG)

auth_app = webapp2.WSGIApplication([
#    ('/auth/signin/start', auth_handlers.SignInHandler),
#    ('/auth/signin/callback', auth_handlers.SignInCallbackHandler),
#    ('/auth/sign_in', auth_handlers.SignInHandler),
], config=appengine_config.WEBAPP2_AUTH_CONFIG)

oauth2_app = webapp2.WSGIApplication([
    ('/oauth2callback', auth_handlers.OAuth2CallbackHandler),
], config=appengine_config.WEBAPP2_AUTH_CONFIG)

api_app = service.service_mappings((
    ('/_api/avatars.*', avatar_services.AvatarService),
    ('/_api/comments.*', comment_services.CommentService),
    ('/_api/filesets.*', fileset_services.FilesetService),
    ('/_api/me.*', user_services.MeService),
    ('/_api/launches.*', launch_services.LaunchService),
    ('/_api/owners.*', owner_services.OwnerService),
    ('/_api/orgs.*', org_services.OrgService),
    ('/_api/projects.*', project_services.ProjectService),
    ('/_api/teams.*', team_services.TeamService),
    ('/_api/users.*', user_services.UserService),
), registry_path='/_api/protorpc')


def domain_middleware(conditions_and_apps):
  def middleware(environ, start_response):
    for condition_func, app in conditions_and_apps:
      if condition_func(environ['SERVER_NAME'], path=environ['PATH_INFO']):
        return app(environ, start_response)
  return middleware


def allowed_user_domains_middleware(app):
  # TODO(jeremydw): Instead of using the App Engine Users API, we should
  # switch this to use OAuth2 integration with Google Accounts. Implement
  # an SSO service for preview domains.
  def middleware(environ, start_response):
    allowed_user_domains = appengine_config.ALLOWED_USER_DOMAINS
    if allowed_user_domains is None:
      return app(environ, start_response)
    user = users.get_current_user()
    if user is None:
      url =  users.create_login_url(environ['PATH_INFO'])
      start_response('302', [('Location', url)])
      return []
    if user.email().split('@')[-1] not in allowed_user_domains:
      start_response('403', [])
      url = users.create_logout_url(environ['PATH_INFO'])
      return ['Forbidden. <a href="{}">Sign out</a>.'.format(url)]
    return app(environ, start_response)
  return middleware


app = allowed_user_domains_middleware(domain_middleware([
    # TODO(jeremydw): Do not run API on user content domain.
    (lambda _, path: path.startswith('/oauth2'), oauth2_app),
    (lambda _, path: path.startswith('/auth'), auth_app),
    (lambda _, path: path.startswith('/_api'), api_app),
    (utils.is_preview_server, server_app),
    (lambda _, path: True, frontend_app),
]))
