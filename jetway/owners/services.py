from protorpc import remote
from jetway import api
from jetway.owners import owners
from jetway.owners import messages


class OwnerService(api.Service):

  @remote.method(messages.CreateOwnerRequest,
                 messages.CreateOwnerResponse)
  def create(self, request):
    try:
      owner = owners.Owner.create(nickname=request.owner.nickname)
    except owners.OwnerExistsError as e:
      raise api.ConflictError(str(e))
    resp = messages.CreateOwnerResponse()
    resp.owner = owner.to_message()
    return resp

  @remote.method(messages.DeleteOwnerRequest,
                 messages.DeleteOwnerResponse)
  def delete(self, request):
    owner = self.get_owner(request)
    owner.delete()
    resp = messages.DeleteOwnerResponse()
    return resp

  @remote.method(messages.SearchOwnerRequest,
                 messages.SearchOwnerResponse)
  def search(self, request):
    results = owners.Owner.search()
    resp = messages.SearchOwnerResponse()
    resp.owners = [e.to_message() for e in results]
    return resp

  @remote.method(messages.UpdateOwnerRequest,
                 messages.UpdateOwnerResponse)
  def update(self, request):
    owner = self.get_owner(request)
    owner.update(request.owner)
    resp = messages.UpdateOwnerResponse()
    resp.owner = owner.to_message()
    return resp

  @remote.method(messages.GetOwnerRequest,
                 messages.GetOwnerResponse)
  def get(self, request):
    owner = self.get_owner(request)
    resp = messages.GetOwnerResponse()
    resp.owner = owner.to_message()
    return resp
