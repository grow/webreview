from protorpc import remote
import httplib


class Error(remote.ApplicationError):
  pass


class ServiceError(remote.ApplicationError):
  status = httplib.BAD_REQUEST


class BadRequestError(remote.ApplicationError):
  status = httplib.BAD_REQUEST


class NotFoundError(ServiceError):
  status = httplib.NOT_FOUND


class ConflictError(ServiceError):
  status = httplib.CONFLICT


class ForbiddenError(ServiceError):
  status = httplib.FORBIDDEN


class UnauthorizedError(ServiceError):
  status = httplib.UNAUTHORIZED
