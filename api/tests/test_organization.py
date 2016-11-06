from unittest import skip

from django.contrib.auth import get_user_model
from django_dynamic_fixture import G
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from api.auth.session_generator import generate_session_params
from api.models import Band, Composition, Member, Session
from api.permissions import renovate_permissions
from api.serializers import MemberSerializer

User = get_user_model()


class CreatePermissionsMixin(object):
    @classmethod
    def setUpTestData(cls):
        renovate_permissions()


class BaseTestCase(CreatePermissionsMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super(BaseTestCase, cls).setUpTestData()
        users = G(User, is_active=True, is_superuser=True, avatar=None, n=2)
        cls.user = users[0]
        cls.only_user = users[1]
        cls.session = G(Session, **generate_session_params(cls.user))
        cls.band = G(Band)
        cls.member = G(Member, user=cls.user)
        cls.composition = G(Composition)


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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(
            response.data,
            MemberSerializer(Member.objects.get(id=response.data['id'])).data
        )
