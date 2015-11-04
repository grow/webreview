from requests import auth
import appengine_config
import requests

BASE = '{}/api'.format(appengine_config.BUILDBOT_URL)


class Error(Exception):
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
    except Exception as e:
      raise Error(e)
    return resp.json()

  def list_branches(self, job_id):
    try:
      resp = requests.get(BASE + '/git/repos/{}/branches'.format(job_id))
    except Exception as e:
      raise Error(e)
    content = resp.json()
    return content

  def get_contents(self, job_id, path=None):
    path = path or '/'
    try:
      resp = requests.get(BASE + '/git/repos/{}/contents{}'.format(job_id, path))
    except Exception as e:
      raise Error(e)
    return resp.json()

  def read_file(self, job_id, path):
    try:
      resp = requests.get(BASE + '/git/repos/{}/raw{}'.format(job_id, path))
    except Exception as e:
      raise Error(e)
    return resp.body

#  def write_file(self, job_id, path, contents):
#    resp = requests.post(BASE + '/jobs/{}/contents/update'.format(job_id))
#    return resp.body
