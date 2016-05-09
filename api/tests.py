from django.contrib.auth import get_user_model
from django_dynamic_fixture import G
from rest_framework.test import APITestCase

from api.auth.session_generator import generate_session_params
from api.models import Session
from api.permissions import renovate_permissions

User = get_user_model()


class CreatePermissionsMixin(object):
    def setUp(self):
        renovate_permissions()


class ViewTestCase(CreatePermissionsMixin, APITestCase):
    def setUp(self):
        super(ViewTestCase, self).setUp()
        self.user = G(User, is_active=True, is_superuser=True)
        self.session = G(Session, **generate_session_params(self.user))

    def test_urls(self):
        self.client.login(username=self.user.username, password=self.user.password)
