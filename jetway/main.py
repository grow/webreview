import appengine_config as config
from google.appengine.api import users
from .auth import handlers as auth_handlers
from .avatars import services as avatar_services
from .filesets import services as fileset_services
from .frontend import handlers as frontend_handlers
from .orgs import services as org_services
from .owners import services as owner_services
from .projects import services as project_services
from .server import handlers as server_handlers
from .server import utils
from .teams import services as team_services
from .users import services as user_services
from protorpc.wsgi import service
import endpoints
import webapp2


frontend_app = webapp2.WSGIApplication([
    ('/avatars/(u|o|p)/(.*)', frontend_handlers.AvatarHandler),
    ('/me/signout', auth_handlers.SignOutHandler),
    ('/[^/]*/[^/]*.git.*', frontend_handlers.GitRedirectHandler),
    ('.*', frontend_handlers.FrontendHandler),
], config=config.WEBAPP2_AUTH_CONFIG)

endpoints_app = endpoints.api_server([
    fileset_services.RequestSigningService,
    fileset_services.NewRequestSigningService,
    fileset_services.LegacyRequestSigningService,
])

server_app = webapp2.WSGIApplication([
    ('.*', server_handlers.RequestHandler),
], config=config.WEBAPP2_AUTH_CONFIG)

auth_app = webapp2.WSGIApplication([
#    ('/auth/signin/start', auth_handlers.SignInHandler),
#    ('/auth/signin/callback', auth_handlers.SignInCallbackHandler),
#    ('/auth/sign_in', auth_handlers.SignInHandler),
], config=config.WEBAPP2_AUTH_CONFIG)

oauth2_app = webapp2.WSGIApplication([
    ('/oauth2callback', auth_handlers.OAuth2CallbackHandler),
], config=config.WEBAPP2_AUTH_CONFIG)

api_app = service.service_mappings((
    ('/_api/avatars.*', avatar_services.AvatarService),
    ('/_api/filesets.*', fileset_services.FilesetService),
    ('/_api/me.*', user_services.MeService),
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
    # Allow project-level permissions to control access to previews.
    # But, require users to be signed in. Use App Engine sign in to avoid
    # building an SSO login system for each preview domain.
    full_path = environ['PATH_INFO']
    if environ['QUERY_STRING']:
        full_path += '?' + environ['QUERY_STRING']
    user = users.get_current_user()
    if utils.is_preview_server(environ['SERVER_NAME']):
      if user is None:
        url = users.create_login_url(full_path)
        # Hack to ensure we display the account chooser.
        url = url.replace('/ServiceLogin', '/a/SelectSession', 1)
        start_response('302', [('Location', url)])
        return []
      return app(environ, start_response)
    allowed_user_domains = config.ALLOWED_USER_DOMAINS
    # If all domains are allowed, continue.
    if allowed_user_domains is None:
      return app(environ, start_response)
    # Redirect anonymous users to login.
    if user is None:
      url = users.create_login_url(full_path)
      # Hack to ensure we display the account chooser.
      url = url.replace('/ServiceLogin', '/a/SelectSession', 1)
      start_response('302', [('Location', url)])
      return []
    # Ban forbidden users.
    if user.email().split('@')[-1] not in allowed_user_domains:
      start_response('403', [])
      url = users.create_logout_url(full_path)
      return ['Forbidden. <a href="{}">Sign out</a>.'.format(url)]
    return app(environ, start_response)
  return middleware


def https_middleware(app):
  def middleware(environ, start_response):
    is_https = environ['wsgi.url_scheme'] == 'https'
    is_preview_server = utils.is_preview_server(environ['SERVER_NAME'])
    if not config.IS_DEV_SERVER:
      if (is_preview_server and config.REQUIRE_HTTPS_FOR_PREVIEWS and not is_https
          or not is_preview_server and config.REQUIRE_HTTPS_FOR_APP and not is_https):
        host = environ['HTTP_HOST']
        if is_preview_server and 'appspot.com' in host and '-dot-' not in host:
          host = host.replace('.', '-dot-', 1)
        url = 'https://' + host + environ['PATH_INFO']
        start_response('302', [('Location', url)])
        return []
    return app(environ, start_response)
  return middleware


app = https_middleware(allowed_user_domains_middleware(domain_middleware([
    # TODO(jeremydw): Do not run API on user content domain.
    (lambda _, path: path.startswith('/oauth2'), oauth2_app),
    (lambda _, path: path.startswith('/auth'), auth_app),
    (lambda _, path: path.startswith('/_api'), api_app),
    (utils.is_preview_server, server_app),
    (lambda _, path: True, frontend_app),
])))
