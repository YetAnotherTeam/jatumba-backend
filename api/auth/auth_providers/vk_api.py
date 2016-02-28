from api.auth.auth_providers.base import BaseProvider
from api.excpetions.api_exceptions import AuthException


class Vk(BaseProvider):
    def get_user_data(self, token):
        request_data = ['first_name', 'last_name', 'email', 'photo', 'id']

        fields = ','.join(set(request_data))
        data = vk_api(self, 'users.get', {
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


def vk_api(backend, method, data):
    data['v'] = '5.45'
    url = 'https://api.vk.com/method/' + method

    try:
        return backend.get_json(url, params=data)
    except (TypeError, KeyError, IOError, ValueError, IndexError):
        return None
