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


def make_url(fileset, project, owner, path=None, multitenant=False,
             include_port=appengine_config.IS_DEV_SERVER):
  preview_hostname = appengine_config.PREVIEW_HOSTNAME
  if include_port:
    preview_hostname += ':{}'.format(os.getenv('SERVER_PORT'))
  if multitenant:
    return 'http://{fileset}--{project}--{owner}.{hostname}'.format(
        fileset=fileset, hostname=preview_hostname,
        owner=owner, project=project)
  else:
    return 'http://{fileset}.{hostname}'.format(
        fileset=fileset, hostname=preview_hostname)
