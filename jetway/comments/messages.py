from protorpc import messages
from jetway.users import messages as user_messages
from protorpc import message_types


class Kind(messages.Enum):
  LAUNCH = 1


class ParentMessage(messages.Message):
  ident = messages.StringField(1)


class CommentMessage(messages.Message):
  ident = messages.StringField(1)
  content = messages.StringField(2)
  created_by = messages.MessageField(user_messages.UserMessage, 3)
  created = message_types.DateTimeField(4)
  kind = messages.EnumField(Kind, 5)
  parent = messages.MessageField(ParentMessage, 6)
  modified = message_types.DateTimeField(7)



###


class CreateCommentRequest(messages.Message):
  comment = messages.MessageField(CommentMessage, 1)

class CreateCommentResponse(messages.Message):
  comment = messages.MessageField(CommentMessage, 1)

class SearchCommentRequest(messages.Message):
  comment = messages.MessageField(CommentMessage, 1)

class SearchCommentResponse(messages.Message):
  comments = messages.MessageField(CommentMessage, 1, repeated=True)

class GetCommentRequest(messages.Message):
  comment = messages.MessageField(CommentMessage, 1)

class GetCommentResponse(messages.Message):
  comment = messages.MessageField(CommentMessage, 1)

class DeleteCommentRequest(messages.Message):
  comment = messages.MessageField(CommentMessage, 1)

class DeleteCommentResponse(messages.Message):
  comment = messages.MessageField(CommentMessage, 1)

class UpdateCommentRequest(messages.Message):
  comment = messages.MessageField(CommentMessage, 1)

class UpdateCommentResponse(messages.Message):
  comment = messages.MessageField(CommentMessage, 1)
