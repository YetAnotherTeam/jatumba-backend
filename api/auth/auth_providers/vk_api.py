from api.auth.auth_providers.base import BaseProvider
from api.exceptions.api_exceptions import AuthException


class VK(BaseProvider):
    request_data = ('first_name', 'last_name', 'email', 'photo', 'id')

    def __init__(self, *args, **kwargs):
        super(VK, self).__init__(args, kwargs)

    def get_user_data(self, token):
        fields = ','.join(self.request_data)
        data = VK_API().request(self, 'users.get', {
            'access_token': token,
            'fields': fields,
        })

        if data and data.get('error'):
            error = data['error']
            msg = error.get('error_msg', 'VK API error')
            raise AuthException(msg)

        if data is None:
            raise AuthException('VK doesn\'t return user data')

        user_data = data['response'][0]
        user_id = user_data.pop('id')
        user_data['user_id'] = str(user_id)
        user_data['network'] = 'vk'

        return user_data


class VK_API:
    version = '5.45'
    url = 'https://api.vk.com/method/%s'

    def request(self, backend, method, data):
        data['v'] = self.version
        try:
            return backend.get_json(self.url, params=data)
        except (TypeError, KeyError, IOError, ValueError, IndexError):
            return None
