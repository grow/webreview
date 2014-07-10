from protorpc import messages
from jetway.orgs import messages as org_messages
from jetway.users import messages as user_messages


class CreateOrgRequest(messages.Message):
  org = messages.MessageField(org_messages.OrgMessage, 1)


class CreateOrgResponse(messages.Message):
  org = messages.MessageField(org_messages.OrgMessage, 1)


class DeleteOrgRequest(messages.Message):
  org = messages.MessageField(org_messages.OrgMessage, 1)


class DeleteOrgResponse(messages.Message):
  pass


class UpdateOrgRequest(messages.Message):
  org = messages.MessageField(org_messages.OrgMessage, 1)


class UpdateOrgResponse(messages.Message):
  org = messages.MessageField(org_messages.OrgMessage, 1)


class GetOrgRequest(messages.Message):
  org = messages.MessageField(org_messages.OrgMessage, 1)


class GetOrgResponse(messages.Message):
  org = messages.MessageField(org_messages.OrgMessage, 1)


class ListOrgsRequest(messages.Message):
  pass


class ListOrgsResponse(messages.Message):
  orgs = messages.MessageField(org_messages.OrgMessage, 1, repeated=True)


class SearchMembersRequest(messages.Message):
  org = messages.MessageField(org_messages.OrgMessage, 1)


class SearchMembersResponse(messages.Message):
  users = messages.MessageField(user_messages.UserMessage, 1, repeated=True)
