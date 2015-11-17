from protorpc import remote
from app import api
from app.avatars import avatars
from app.avatars import messages


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
