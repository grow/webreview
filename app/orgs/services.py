from app import api
from app.groups import groups
from app.orgs import orgs
from app.orgs import service_messages
from app.users import users
from protorpc import remote
import logging


class OrgService(api.Service):

  @remote.method(
      service_messages.CreateOrgRequest,
      service_messages.CreateOrgResponse)
  @api.me_required
  def create(self, request):
    try:
      org = orgs.Org.create(request.org.nickname, self.me)
    except Exception as e:
      logging.exception('Problem creating org.')
      raise remote.ApplicationError(str(e))
    message = service_messages.CreateOrgResponse()
    message.org = org.to_message()
    return message

  @remote.method(
      service_messages.GetOrgRequest,
      service_messages.GetOrgResponse)
  def get(self, request):
    org = orgs.Org.get(request.org.nickname)
    message = service_messages.GetOrgResponse()
    message.org = org.to_message()
    return message

  @remote.method(
      service_messages.DeleteOrgRequest,
      service_messages.DeleteOrgResponse)
  def delete(self, request):
    try:
      org = orgs.Org.get(request.org.nickname)
      org.delete()
    except Exception as e:
      raise remote.ApplicationError(str(e))
    message = service_messages.DeleteOrgResponse()
    return message

  @remote.method(
      service_messages.ListOrgsRequest,
      service_messages.ListOrgsResponse)
  def list(self, request):
    results = orgs.Org.list()
    message = service_messages.ListOrgsResponse()
    message.orgs = [org.to_message() for org in results]
    return message

  @remote.method(
      service_messages.UpdateOrgRequest,
      service_messages.UpdateOrgResponse)
  def update(self, request):
    org = orgs.Org.get(request.org.nickname)
    org.update_from_message(request.org)
    message = service_messages.UpdateOrgResponse()
    message.org = org.to_message()
    return message

  @remote.method(
      service_messages.SearchMembersRequest,
      service_messages.SearchMembersResponse)
  def search_members(self, request):
    org = orgs.Org.get(request.org.nickname)
    results = org.search_members()
    message = service_messages.SearchMembersResponse()
    message.users = [user.to_message() for user in results]
    return message

  @remote.method(service_messages.GetOrgRequest,
                 service_messages.GroupResponse)
  def get_group(self, request):
    org = orgs.Org.get(request.org.nickname)
#    self._get_policy(project).authorize_read()
    resp = service_messages.GroupResponse()
    resp.group = org.group.to_message()
    return resp

  @remote.method(service_messages.MembershipRequest,
                 service_messages.GroupResponse)
  def update_membership(self, request):
    org = self._get_org(request)
#    self._get_policy(org).authorize_admin()
    try:
      org.group.update_membership(request.membership)
    except groups.Error as e:
      raise api.Error(str(e))
    resp = service_messages.GroupResponse()
    resp.group = org.group.to_message()
    return resp

  @remote.method(service_messages.MembershipRequest,
                 service_messages.GroupResponse)
  def create_membership(self, request):
    org = self._get_org(request)
#    self._get_policy(org).authorize_admin()
    try:
      org.group.create_membership(request.membership)
    except groups.Error as e:
      raise api.Error(str(e))
    resp = service_messages.GroupResponse()
    resp.group = org.group.to_message()
    return resp
