from django_dynamic_fixture import G
from rest_framework.test import APITestCase

from api.models import CompositionVersion, DiffCompositionVersion, Track


class BaseTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.composition_version = G(CompositionVersion)
        cls.tracks_count = 5
        G(Track, composition_version=cls.composition_version, n=cls.tracks_count)

    def test_copy_diff_composition_version_from_composition_version(self):
        diff_composition_version = DiffCompositionVersion.copy_from_version(
            self.composition_version
        )
        self.assertEquals(diff_composition_version.tracks.count(), self.tracks_count)
        self.assertEquals(
            diff_composition_version.tracks.count(),
            self.composition_version.tracks.count()
        )
