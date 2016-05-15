from unittest import skip

from django.contrib.auth import get_user_model
from django_dynamic_fixture import G
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from api.auth.session_generator import generate_session_params
from api.models import Session, Band, Member, Composition
from api.permissions import renovate_permissions
from api.serializers import MemberSerializer

User = get_user_model()


class CreatePermissionsMixin(object):
    def setUp(self):
        renovate_permissions()


class BaseTestCase(CreatePermissionsMixin, APITestCase):
    def setUp(self):
        super(BaseTestCase, self).setUp()
        users = G(User, is_active=True, is_superuser=True, avatar=None, n=2)
        self.user = users[0]
        self.only_user = users[1]
        self.session = G(Session, **generate_session_params(self.user))
        self.band = G(Band)
        self.member = G(Member, user=self.user)
        self.composition = G(Composition)


@skip('Not implemented')
class ViewTestCase(BaseTestCase):
    def test_urls(self):
        self.client.login(username=self.user.username, password=self.user.password)


class MemberTestCase(BaseTestCase):
    def test_create(self):
        self.client.credentials(HTTP_TOKEN=self.session.access_token)
        response = self.client.post(
            reverse('member-list'),
            {
                'band': self.band.id
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data,
            MemberSerializer(Member.objects.get(id=response.data['id'])).data
        )
