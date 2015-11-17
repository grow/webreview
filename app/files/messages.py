from protorpc import messages


class Verb(messages.Enum):
  PUT = 0
  GET = 1
  DELETE = 2


class Params(messages.Message):
  google_access_id = messages.StringField(1)
  expires = messages.StringField(2)
  signature = messages.StringField(3)


class Headers(messages.Message):
  content_type = messages.StringField(1)
  content_length = messages.StringField(2)
  content_md5 = messages.StringField(3)


class SignedRequest(messages.Message):
  url = messages.StringField(1)
  params = messages.MessageField(Params, 2)
  headers = messages.MessageField(Headers, 3)
  path = messages.StringField(4)
  verb = messages.EnumField(Verb, 5)


class UnsignedRequest(messages.Message):
  verb = messages.EnumField(Verb, 1)
  path = messages.StringField(2)
  headers = messages.MessageField(Headers, 3)


class FileMessage(messages.Message):
  path = messages.StringField(1)
