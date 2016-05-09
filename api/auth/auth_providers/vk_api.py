from rest_framework.exceptions import AuthenticationFailed

from api.auth.auth_providers.base import BaseProvider


class VK(BaseProvider):
    request_data = ('first_name', 'last_name', 'email', 'photo', 'id')

    def __init__(self, *args, **kwargs):
        super(VK, self).__init__(args, kwargs)
        self.fields = ','.join(self.request_data)
        self.vk_api = VK_API()

    def get_user_data(self, token):
        user_data = self.vk_api.request(self, 'users.get', {
            'access_token': token,
            'fields': self.fields,
        })

        if user_data and user_data.get('error'):
            error = user_data['error']
            msg = error.get('error_msg', 'VK API error')
            raise AuthenticationFailed(msg)

        if user_data is None:
            raise AuthenticationFailed('VK doesn\'t return user data')
        try:
            user_data = user_data['response'][0]
        except IndexError:
            raise AuthenticationFailed('VK doesn\'t find user')
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
            return backend.get_json(self.url % method, params=data)
        except (TypeError, KeyError, IOError, ValueError, IndexError):
            return None
