from rest_framework.exceptions import AuthenticationFailed

from api.auth.auth_providers.base import BaseProvider


class FB(BaseProvider):
    request_data = ('first_name', 'last_name', 'email', 'id')

    def __init__(self, *args, **kwargs):
        super(FB, self).__init__(args, kwargs)
        self.fields = ','.join(self.request_data)
        self.fb_api = FB_API()

    def get_user_data(self, token):
        user_data = self.fb_api.request(
            self,
            'me',
            {
                'access_token': token,
                'fields': self.fields,
            }
        )

        if user_data and user_data.get('error'):
            error = user_data['error']
            msg = error.get('error_msg', 'FB API error')
            raise AuthenticationFailed(msg)

        if user_data is None:
            raise AuthenticationFailed('FB doesn\'t return user data')

        user_id = user_data.pop('id')
        user_data['user_id'] = str(user_id)
        user_data['network'] = 'fb'

        return user_data


class FB_API:
    URL = 'https://graph.facebook.com/v2.5/%s'

    def request(self, backend, method, data):
        try:
            return backend.get_json(self.URL % method, params=data)
        except (TypeError, KeyError, IOError, ValueError, IndexError):
            return None
