from django_dynamic_fixture import G
from rest_framework.test import APITestCase

from api.models import CompositionVersion, DiffCompositionVersion, Track


class BaseTestCase(APITestCase):
    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.composition_version = G(CompositionVersion)
        self.tracks_count = 5
        G(Track, composition_version=self.composition_version, n=self.tracks_count)

    def test_copy_diff_composition_version_from_composition_version(self):
        diff_composition_version = DiffCompositionVersion.copy_from_version(
            self.composition_version
        )
        self.assertEquals(diff_composition_version.tracks.count(), self.tracks_count)
        self.assertEquals(
            diff_composition_version.tracks.count(),
            self.composition_version.tracks.count()
        )
