from protorpc import messages
from app.owners import messages as owner_messages
from app.projects import messages as project_messages


class CreateUploadUrlRequest(messages.Message):
  owner = messages.MessageField(owner_messages.OwnerMessage, 1)
  project = messages.MessageField(project_messages.ProjectMessage, 2)


class CreateUploadUrlResponse(messages.Message):
  upload_url = messages.StringField(1)
