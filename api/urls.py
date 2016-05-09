from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from api.views import *

router = DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'band', BandViewSet)
router.register(r'member', MemberViewSet)
router.register(r'composition', CompositionViewSet)
router.register(r'composition_version', CompositionVersionViewSet)
router.register(r'instrument', InstrumentViewSet)
router.register(r'fork', ForkViewSet)

urlpatterns = [
    url(r'sign_up/vk/', VKAuthView.as_view(), name='sign_up_vk'),
    url(r'sign_up/fb/', FBAuthView.as_view(), name='sign_up_fb'),
    url(r'token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    url(r'', include(router.urls))
]
