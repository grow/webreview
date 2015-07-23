from apiclient import discovery
from google.appengine.api import memcache
from jetway.users import users
from oauth2client import appengine
from webapp2_extras import auth as webapp2_auth
from webapp2_extras import security
from webapp2_extras import sessions
import appengine_config
import httplib2
import json
import logging
import os
import webapp2


decorator = appengine.OAuth2DecoratorFromClientSecrets(
    filename=appengine_config.client_secrets_path,
    scope=appengine_config.OAuth.SCOPES)



def get_google_storage_flow(**kwargs):
  scheme = os.getenv('wsgi.url_scheme')
  origin = os.getenv('HTTP_HOST')
  redirect_uri = '{}://{}/oauth2/callback/googlestorage'.format(scheme, origin)
  scope = ['https://www.googleapis.com/auth/devstorage.full_control']
  secrets = appengine_config.client_secrets['web']
  return appengine.OAuth2WebServerFlow(
      secrets['client_id'],
      secrets['client_secret'],
      scope,
      redirect_uri=redirect_uri,
      user_agent='Jetway', **kwargs)



class SessionUser(object):

  def __init__(self, sid):
    self.sid = sid

  def user_id(self):
    # Provides compatibility with oauth2client's {_build|_parse}_state_value.
    return self.sid



class SessionHandler(webapp2.RequestHandler):
  """A request handler that supports webapp2 sessions."""

  def dispatch(self):
    """Wraps the dispatch method to add session handling."""
    self.session_store = sessions.get_store(request=self.request)
    self.decorator = decorator

    # Add the user's credentials to the decorator if we have them.
    if self.me:
      self.decorator.credentials = self.decorator._storage_class(
          model=self.decorator._credentials_class,
          key_name='user:{}'.format(self.me.user_id()),
          property_name=self.decorator._credentials_property_name).get()
    else:
      # Create a session ID for the session if it does not have one already.
      # This is used to create an opaque string that can be passed to the OAuth2
      # authentication server via the 'state' parameter.
      if not self.session.get('sid'):
        self.session['sid'] = security.generate_random_string(entropy=128)

      # Store the state for the session user in a parameter on the flow.
      # We only need to do this if we're not logged in.
      self.decorator._create_flow(self)
      session_user = SessionUser(self.session['sid'])
      logging.info(self.decorator.flow.params)
      self.decorator.flow.params['state'] = appengine._build_state_value(
          self, session_user)

    try:
      webapp2.RequestHandler.dispatch(self)
    finally:
      self.session_store.save_sessions(self.response)

  def create_sign_out_url(self):
    return '/me/signout'

  def create_sign_in_url(self):
    return self.decorator.authorize_url()

  @webapp2.cached_property
  def auth(self):
    return webapp2_auth.get_auth()

  @webapp2.cached_property
  def me(self):
    from google.appengine.api import users as users_api
    user = users_api.get_current_user()
    if user:
      return users.User.get_by_email(user.email())
    user_dict = self.auth.get_user_by_session()
    if user_dict:
      return users.User.get_by_auth_id(str(user_dict['user_id']))

  @webapp2.cached_property
  def session(self):
    return self.session_store.get_session()

  def sign_out(self):
    self.auth.unset_session()
    try:
      self.redirect(self.request.referer)
    except AttributeError:  # When there is no referer.
      self.redirect('/')


class OAuth2CallbackHandler(SessionHandler):
  """Callback handler for OAuth2 flow."""

  def get(self):
    # In order to use our own ConnectedUser class and webapp2 sessions
    # for user management instead of the App Engine Users API (which requires
    # showing a very ugly sign in page and requires the user to authorize
    # Google twice, essentially), we've created our own version of oauth2client's
    # OAuth2CallbackHandler.
    error = self.request.get('error')
    if error:
      message = self.request.get('error_description', error)
      text = 'Authorization request failed: {}'
      self.response.out.write(text.format(message))
      return

    # Resume the OAuth flow.
    decorator._create_flow(self)
    credentials = decorator.flow.step2_exchange(self.request.params)

    # Get a Google Account ID for the user that just OAuthed in.
    http = credentials.authorize(httplib2.Http(memcache))
    service = discovery.build('oauth2', 'v2', http=httplib2.Http(memcache))

    # Keys are: name, email, given_name, family_name, link, locale, id,
    # gender, verified_email (which is a bool), picture (url).
    data = service.userinfo().v2().me().get().execute(http=http)
    auth_id = 'google:{}'.format(data['id'])

    # If the user is returning, try and find an existing ConnectedUser.
    # If the user is signing in for the first time, create a ConnectedUser.
    user = users.User.get_by_auth_id(auth_id)
    if user is None:
      nickname = users.User.create_unique_username(data['email'])
      data.pop('id', None)
      unique_properties = ['nickname', 'email']
      ok, user = users.User.create_user(
          auth_id, unique_properties=unique_properties, nickname=nickname,
          **data)
      if not ok:
        logging.exception('Invalid values: {}'.format(user))
        self.error(500)
        return

    # Store the ConnectedUser in the session.
    self.auth.set_session({'user_id': auth_id}, remember=True)

    session_user = SessionUser(self.session['sid'])
    redirect_uri = appengine._parse_state_value(
        str(self.request.get('state')), session_user)

    # Store the user's credentials for later possible use.
    storage = decorator._storage_class(
        model=decorator._credentials_class,
        key_name='user:{}'.format(user.user_id()),
        property_name=decorator._credentials_property_name)
    storage.put(credentials)

    # Adjust the redirect uri in case this callback occurred as part of an
    # authenticated request to get some data.
    if decorator._token_response_param and credentials.token_response:
      resp = json.dumps(credentials.token_response)
      redirect_uri = appengine.util._add_query_parameter(
          redirect_uri, decorator._token_response_param, resp)

    self.redirect(redirect_uri)


class SignOutHandler(SessionHandler):

  def get(self):
    self.sign_out()
