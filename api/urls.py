from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from api.views import *

router = DefaultRouter()
router.register(r'band', BandViewSet)
router.register(r'member', BandMembersViewSet)
router.register(r'composition', CompositionViewSet)
router.register(r'user', UserViewSet)
router.register(r'instrument', InstrumentViewSet)
router.register(r'track/history', TrackHistoryView)
router.register(r'track', TrackViewSet)

urlpatterns = [
    url(r'sign_up/vk/', VKAuthView.as_view()),
    url(r'sign_up/fb/', FBAuthView.as_view()),
    url(r'token/refresh/', RefreshToken.as_view()),
    url(r'token/is_auth', IsAuth.as_view()),
    url(r'', include(router.urls))
]
