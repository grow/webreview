from protorpc import remote
from jetway import api
from jetway.orgs import orgs
from jetway.orgs import service_messages
from jetway.users import users
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
