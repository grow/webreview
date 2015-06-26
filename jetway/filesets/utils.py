from google.appengine.api import mail
from jetway.users import users
import appengine_config
import cStringIO
import jinja2
import os
import premailer

_path = os.path.join(os.path.dirname(__file__), 'templates')
_loader = jinja2.FileSystemLoader(_path)
_env = jinja2.Environment(loader=_loader, autoescape=True, trim_blocks=True)


def send_finalized_email(fileset):
  subject = 'Preview: {}'.format(str(fileset))
  template_name = 'finalized_email.html'
#  users = fileset.project.list_users_to_notify()
#  emails = [user.email for user in users]
  emails = ['jeremydw@google.com']
  if not emails:
    return

  kwargs = {
    'config': appengine_config,
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
