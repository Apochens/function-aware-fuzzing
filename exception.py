class FAException(Exception):
    pass


class CoverageError(FAException):
    pass


class FnException(FAException):
    pass


class FnExecFailed(FnException):
    """Throw this exception when the client fails to execute the given API call"""
    pass


class FnNotFound(FnException):
    """
    Throw this exception when the given API call is not supported by the client.
    Usually the API name in the given seed is wrong.
    """
    pass


class ServerException(FAException):
    pass


class ServerNotStarted(ServerException):
    pass


class ServerTerminated(ServerException):
    pass