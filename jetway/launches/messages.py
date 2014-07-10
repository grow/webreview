from protorpc import messages
from protorpc import message_types
from jetway.projects import messages as project_messages
from jetway.filesets import messages as fileset_messages
from jetway.owners import messages as owner_messages
from jetway.users import messages as user_messages


class ApprovalMessage(messages.Message):
  user = messages.MessageField(user_messages.UserMessage, 1)
  created = message_types.DateTimeField(2)


class ReviewerMessage(messages.Message):
  user = messages.MessageField(user_messages.UserMessage, 1)
  is_approved = messages.BooleanField(2)
  review_required = messages.BooleanField(3)
  created_by = messages.MessageField(user_messages.UserMessage, 4)


class LaunchMessage(messages.Message):
  description = messages.StringField(1)
  ident = messages.StringField(2)
  owner = messages.MessageField(owner_messages.OwnerMessage, 3)
  project = messages.MessageField(project_messages.ProjectMessage, 4)
  created_by = messages.MessageField(user_messages.UserMessage, 5)
  title = messages.StringField(6)
  created = message_types.DateTimeField(7)
  ttl = message_types.DateTimeField(8)
  reviewers = messages.MessageField(ReviewerMessage, 9, repeated=True)
  num_comments = messages.IntegerField(11)
  fileset = messages.MessageField(fileset_messages.FilesetMessage, 12)
  approvals = messages.MessageField(ApprovalMessage, 13, repeated=True)


###


class CreateLaunchRequest(messages.Message):
  launch = messages.MessageField(LaunchMessage, 1)

class CreateLaunchResponse(messages.Message):
  launch = messages.MessageField(LaunchMessage, 1)

class SearchLaunchRequest(messages.Message):
  launch = messages.MessageField(LaunchMessage, 1)

class SearchLaunchResponse(messages.Message):
  launches = messages.MessageField(LaunchMessage, 1, repeated=True)

class GetLaunchRequest(messages.Message):
  launch = messages.MessageField(LaunchMessage, 1)

class GetLaunchResponse(messages.Message):
  launch = messages.MessageField(LaunchMessage, 1)

class DeleteLaunchRequest(messages.Message):
  launch = messages.MessageField(LaunchMessage, 1)

class DeleteLaunchResponse(messages.Message):
  launch = messages.MessageField(LaunchMessage, 1)

class UpdateLaunchRequest(messages.Message):
  launch = messages.MessageField(LaunchMessage, 1)

class UpdateLaunchResponse(messages.Message):
  launch = messages.MessageField(LaunchMessage, 1)

class CreateApprovalRequest(messages.Message):
  launch = messages.MessageField(LaunchMessage, 1)

class CreateApprovalResponse(messages.Message):
  launch = messages.MessageField(LaunchMessage, 1)

class DeleteApprovalRequest(messages.Message):
  launch = messages.MessageField(LaunchMessage, 1)

class DeleteApprovalResponse(messages.Message):
  launch = messages.MessageField(LaunchMessage, 1)
