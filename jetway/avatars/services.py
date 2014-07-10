from protorpc import remote
from jetway import api
from jetway.avatars import avatars
from jetway.avatars import messages


class AvatarService(api.Service):

  @remote.method(messages.CreateUploadUrlRequest,
                 messages.CreateUploadUrlResponse)
  def create_upload_url(self, request):
    owner = self.get_owner(request) if request.owner else None
    project = self.get_project(request) if request.project else None
    entity = owner or project
    resp = messages.CreateUploadUrlResponse()
    resp.upload_url = avatars.Avatar.create_upload_url(entity)
    return resp
