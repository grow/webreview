from requests import auth
import appengine_config
import requests

BASE = '{}/api'.format(appengine_config.BUILDBOT_URL)


class Error(Exception):
  pass


class ConnectionError(Error):
  pass


class IntegrationError(Error):
  pass


class Buildbot(object):

  @property
  def env(self):
    return {
        'WEBREVIEW_API_KEY': appengine_config.BUILDBOT_API_KEY,
    }

  @property
  def auth(self):
    return auth.HTTPBasicAuth(
        appengine_config.BUILDBOT_USERNAME,
        appengine_config.BUILDBOT_PASSWORD)

  def create_job(self, git_url, remote):
    data = {
        'git_url': git_url,
        'remote': remote,
        'env': self.env,
    }
    try:
      resp = requests.post(BASE + '/jobs', json=data, auth=self.auth)
      resp.raise_for_status()
    except Exception as e:
      raise ConnectionError(e)
    content = resp.json()
    if 'error' in content:
      raise IntegrationError(content['error'])
    return content

  def get_job(self, job_id):
    try:
      resp = requests.get(BASE + '/jobs/{}'.format(job_id), auth=self.auth)
      resp.raise_for_status()
    except Exception as e:
      raise ConnectionError(e)
    content = resp.json()
    if 'error' in content:
      raise IntegrationError(content['error'])
    return content

  def get_contents(self, job_id, path=None, ref=None):
    path = path or '/'
    try:
      request_path = BASE + '/git/repos/{}/contents{}'.format(job_id, path)
      resp = requests.get(request_path, auth=self.auth)
      resp.raise_for_status()
    except Exception as e:
      raise ConnectionError(e)
    content = resp.json()
    if 'error' in content:
      raise IntegrationError(content['error'])
    return content

  def read_file(self, job_id, path, ref):
    try:
      request_path = BASE + '/git/repos/{}/raw/{}{}'.format(job_id, ref, path)
      resp = requests.get(request_path, auth=self.auth)
      resp.raise_for_status()
    except Exception as e:
      raise ConnectionError(e)
    return resp.content

  def write_file(self, job_id, path, contents, message, ref, sha, committer, author):
    data = {
        'branch': ref,
        'path': path,
        'message': message,
        'content': contents,
        'sha': sha,
        'committer': committer,
        'author': author,
    }
    try:
      resp = requests.post(
          BASE + '/jobs/{}/contents/update'.format(job_id),
          json=data,
          auth=self.auth)
      resp.raise_for_status()
    except Exception as e:
      raise ConnectionError(e)
    result = resp.json()
    if 'error' in result:
      raise IntegrationError(result['error'])
    return result
