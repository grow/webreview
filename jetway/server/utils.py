import appengine_config
import os
import re

_HOSTNAME_RE = re.compile('^(?:(.*)--)?(.*)--([^\.]*)\.')


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


def make_url(fileset, project, owner, path=None,
             multitenant=appengine_config.jetway_config['options']['multitenant'],
             include_port=appengine_config.IS_DEV_SERVER):
  preview_hostname = appengine_config.PREVIEW_HOSTNAME
  scheme = os.getenv('wsgi.url_scheme', 'http')
  if include_port:
    preview_hostname += ':{}'.format(os.getenv('SERVER_PORT'))
  if scheme == 'https' and 'appspot.com' in preview_hostname:
    sep = '-dot-'
  else:
    sep = '.'
  if multitenant:
    return '{scheme}://{fileset}--{project}--{owner}{sep}{hostname}'.format(
        scheme=scheme, fileset=fileset, sep=sep, hostname=preview_hostname,
        owner=owner, project=project)
  else:
    return '{scheme}://{fileset}{sep}{hostname}'.format(
        scheme=scheme, fileset=fileset, sep=sep, hostname=preview_hostname)
