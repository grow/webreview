from google.appengine.api import mail
from jetway.server import utils as server_utils
from jetway.users import users
import appengine_config
import cStringIO
import jinja2
import logging
import os
import urllib2
import premailer

_path = os.path.join(os.path.dirname(__file__), 'templates')
_loader = jinja2.FileSystemLoader(_path)
_env = jinja2.Environment(loader=_loader, autoescape=True, trim_blocks=True)


def invoke_screenshots(fileset):
  url = server_utils.make_url(None, None, None, ident='screenshots')
  fileset_base_url = url + '/?manifestUrl=' + fileset.url
  urllib2.urlopen(fileset_base_url).read()
  logging.info('Invoked screenshots -> {}'.format(fileset_base_url))


def send_finalized_email(fileset):
  subject = 'Preview: {}'.format(str(fileset))
  template_name = 'finalized_email.html'
  watchers = fileset.project.list_watchers()
  if not watchers:
    return
  emails = [watcher.user.email for watcher in watchers]
  if not emails:
    return

  kwargs = {
      'appengine_config': appengine_config,
      'config': appengine_config.jetway_config,
      'fileset': fileset,
  }
  if fileset.commit and fileset.commit.author:
    kwargs['author'] = users.User.get_by_email(fileset.commit.author.email)

  sender = appengine_config.EMAIL_SENDER
  template = _env.get_template(template_name)
  content = template.render(kwargs)
  html = premailer.transform(content)
  fp = cStringIO.StringIO()
  fp.seek(0)
  emails = [email for email in emails if email is not None]
  message = mail.EmailMessage(sender=sender, subject=subject)
  message.to = list(set([email.strip() for email in emails[:10]]))
  message.html = html
  message.send()
