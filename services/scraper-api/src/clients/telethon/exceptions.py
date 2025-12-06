class TelethonClientError(Exception):
    pass


class TelethonNotAuthorizedError(TelethonClientError):
    pass
