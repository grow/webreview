import appengine_config
import os
import re

_HOSTNAME_RE = re.compile('^(?:(.*)--)?(.*)--([^\.]*)\.')


def is_avatar_request(hostname):
  return re.match('^avatars-.-dot-', hostname)


def is_preview_server(hostname, path=None):
  return (hostname.endswith(appengine_config.PREVIEW_HOSTNAME)
          and hostname != appengine_config.PREVIEW_HOSTNAME
          and not re.match('^avatars\d-dot-', hostname))


def parse_hostname(hostname, path=None, multitenant=False):
  """Returns (fileset, project, owner) parsed from a hostname."""
  hostname = hostname.replace('-dot-', '.')
  preview_hostname = appengine_config.PREVIEW_HOSTNAME
  hostname = hostname.replace(preview_hostname, '')
  results = _HOSTNAME_RE.findall(hostname)
  if not results:
    if multitenant:
      return None
    if not multitenant:
      hostname = hostname.rstrip('.')
      return (hostname, ) if hostname else None
  return tuple(part if part else None for part in results[0])


def make_subdomain(name, project, owner, ident=None, multitenant=False):
  if multitenant:
    return '{name}--{project}--{owner}'.format(
        name=name, project=project, owner=owner)
  elif name:
    return name
  return ident


def make_url(name, project, owner, path=None,
             multitenant=False,
             include_port=appengine_config.IS_DEV_SERVER,
             ident=None):
  preview_hostname = appengine_config.PREVIEW_HOSTNAME
  scheme = os.getenv('wsgi.url_scheme', 'http')
  if include_port:
    preview_hostname += ':{}'.format(os.getenv('SERVER_PORT'))
  if scheme == 'https' and 'appspot.com' in preview_hostname:
    sep = '-dot-'
  else:
    sep = '.'
  subdomain = make_subdomain(name, project, owner, ident=ident, multitenant=multitenant)
  return '{scheme}://{subdomain}{sep}{hostname}'.format(
      scheme=scheme, subdomain=subdomain, sep=sep, hostname=preview_hostname)
