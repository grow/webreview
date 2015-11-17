from app import api
from app.comments import messages
from app.comments import comments
from protorpc import remote


class CommentService(api.Service):

  def _get_comment(self, request):
    try:
      return comments.Comment.get(request.comment.ident)
    except comments.CommentDoesNotExistError as e:
      raise api.NotFoundError(str(e))

  def _get_parent(self, request):
    return comments.Comment.get_parent(request.comment)

  @remote.method(messages.CreateCommentRequest,
                 messages.CreateCommentResponse)
  @api.me_required
  def create(self, request):
    parent = self._get_parent(request)
    comment = comments.Comment.create(parent, created_by=self.me,
                                      content=request.comment.content,
                                      kind=request.comment.kind)
    resp = messages.CreateCommentResponse()
    resp.comment = comment.to_message()
    return resp

  @remote.method(messages.DeleteCommentRequest,
                 messages.DeleteCommentResponse)
  @api.me_required
  def delete(self, request):
    comment = self._get_comment(request)
    comment.delete()
    resp = messages.DeleteCommentResponse()
    return resp

  @remote.method(messages.SearchCommentRequest,
                 messages.SearchCommentResponse)
  def search(self, request):
    parent = self._get_parent(request)
    results = comments.Comment.search(parent=parent, kind=request.comment.kind)
    resp = messages.SearchCommentResponse()
    resp.comments = [comment.to_message() for comment in results]
    return resp
