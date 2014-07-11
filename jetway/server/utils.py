import appengine_config
import os
import re

_HOSTNAME_RE = re.compile('^(?:(.*)--)?(.*)--([^\.]*)\.')


def parse_hostname(hostname, path=None):
  """Returns (fileset, project, owner) parsed from a hostname."""
  preview_hostname = appengine_config.PREVIEW_HOSTNAME
  hostname = hostname.replace(preview_hostname, '')
  hostname = hostname.replace('-dot-', '.')
  results = _HOSTNAME_RE.findall(hostname)
  if not results:
    hostname = hostname.rstrip('.')
    return (hostname, ) if hostname else None
  # Convert empty string to None.
  return tuple(part if part else None for part in results[0])


def make_url(fileset, project, owner, path=None):
  preview_hostname = appengine_config.PREVIEW_HOSTNAME
  if appengine_config.IS_DEV_SERVER:
    preview_hostname += ':{}'.format(os.getenv('SERVER_PORT'))
  return 'http://{fileset}--{project}--{owner}.{hostname}'.format(
      fileset=fileset, hostname=preview_hostname,
      owner=owner, project=project)
