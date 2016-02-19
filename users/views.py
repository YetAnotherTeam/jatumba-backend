from django.http import HttpResponse
from oauth2_provider.views import ProtectedResourceView


class HelloView(ProtectedResourceView):
    """
    A GET endpoint that needs OAuth2 authentication
    """
    def get(self, request, *args, **kwargs):
        return HttpResponse('Hello, World!')
