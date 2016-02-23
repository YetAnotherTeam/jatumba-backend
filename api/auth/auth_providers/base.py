from requests import request
from api.excpetions.api_exceptions import AuthException


class BaseProvider:
    def __init__(self, key='', secret=''):
        self.key = key
        self.secret = secret

    def get_key_and_secret(self):
        return self.key, self.secret

    def request(self, url, method='GET', *args, **kwargs):
        try:
            response = request(method, url, **kwargs)
        except ConnectionError as err:
            raise AuthException(str(err))
        response.raise_for_status()
        return response

    def get_json(self, url, *args, **kwargs):
        return self.request(url, *args, **kwargs).json()
