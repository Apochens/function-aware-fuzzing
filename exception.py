class FAException(Exception):
    pass


class CoverageError(FAException):
    pass



"""
Exceptions related to Fn
"""

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


"""
Exceptions related to Server
"""

class ServerException(FAException):
    pass


class ServerNotStarted(ServerException):
    pass


class ServerTerminated(ServerException):
    pass


class ServerConfigNotFound(ServerException):
    pass


class ServerAbnormallyExited(ServerException):
    pass


"""
Exceptions related to Seed
"""

class SeedException(FAException):
    pass


class SeedDryRunTimeout(SeedException):
    pass