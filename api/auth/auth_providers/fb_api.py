from api.auth.auth_providers.base import BaseProvider
from api.excpetions.api_exceptions import AuthException


class Fb(BaseProvider):
    def get_user_data(self, token):
        request_data = ['first_name', 'last_name', 'email', 'id']

        fields = ','.join(set(request_data))
        user_data = fb_api(self, 'me', {
            'access_token': token,
            'fields': fields,
        })

        if user_data and user_data.get('error'):
            error = user_data['error']
            msg = error.get('error_msg', 'FB API error')
            raise AuthException(msg)

        if user_data is None:
            raise AuthException('FB doesn\'t return user data')

        user_id = user_data.pop('id')
        user_data['user_id'] = str(user_id)
        user_data['network'] = 'fb'

        return user_data


def fb_api(backend, method, data):
    data['v'] = '5.45'
    url = 'https://graph.facebook.com/v2.5/' + method

    try:
        return backend.get_json(url, params=data)
    except (TypeError, KeyError, IOError, ValueError, IndexError):
        return None
