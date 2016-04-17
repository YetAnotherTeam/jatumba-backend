from requests import request
from rest_framework.exceptions import AuthenticationFailed


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
            raise AuthenticationFailed(str(err))
        response.raise_for_status()
        return response

    def get_json(self, url, *args, **kwargs):
        return self.request(url, *args, **kwargs).json()
