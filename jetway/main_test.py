from jetway import main
from jetway import testing
from jetway.owners import owners
from jetway.projects import projects
from jetway.users import users
import os
import unittest
import webapp2


class FrontendAppTestCase(testing.BaseTestCase):

  def test_frontend_app(self):
    req = webapp2.Request.blank('/')
    resp = req.get_response(main.frontend_app)
    self.assertEqual(resp.status_int, 200)


class ServerAppTestCase(testing.BaseTestCase):

  def test_server_app(self):
    server_name = 'fileset--project--owner.example.com'
    os.environ['SERVER_NAME'] = server_name

    user = users.User.create('user')
    owner = owners.Owner(user=user)
    project = projects.Project.create(owner, 'project', created_by=user)
    project.create_fileset('fileset')

    req = webapp2.Request.blank('/')
    resp = req.get_response(main.server_app)
    self.assertEqual(resp.status_int, 404)
    self.assertNotIn('X-AppEngine-BlobKey', resp.headers)


class ApiAppTestCase(testing.BaseTestCase):

  def test_api_app(self):
    headers = {'Content-Type': 'application/json'}
    req = webapp2.Request.blank('/_api/protorpc.services', headers=headers,
                                method='POST')
    resp = req.get_response(main.app)
    self.assertEqual(resp.status_int, 200)
    self.assertIn('services', resp.json)


if __name__ == '__main__':
  unittest.main()
