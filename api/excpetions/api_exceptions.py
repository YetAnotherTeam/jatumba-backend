class ApiException(BaseException):
    pass


class AuthException(ApiException):
    error_code = 401

    def __init__(self, message="problem with auth"):
        self.message = message

    def __str__(self):
        return self.message
