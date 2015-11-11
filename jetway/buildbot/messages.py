from protorpc import messages


class CommitMessage(messages.Message):
  sha = messages.StringField(1)


class BranchMessage(messages.Message):
  name = messages.StringField(1)
  commit = messages.MessageField(CommitMessage, 2)
  ident = messages.StringField(3)
