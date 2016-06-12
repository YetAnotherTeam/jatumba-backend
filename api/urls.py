from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from api.views import (
    BandViewSet, CompositionVersionViewSet, CompositionViewSet, FBAuthView, ForkViewSet,
    InstrumentViewSet, MemberViewSet, SessionViewSet, UserViewSet, VKAuthView
)

router = DefaultRouter()
router.register(r'user', UserViewSet, base_name='user')
router.register(r'band', BandViewSet, base_name='band')
router.register(r'member', MemberViewSet)
router.register(r'composition', CompositionViewSet, base_name='composition')
router.register(r'composition_version', CompositionVersionViewSet)
router.register(r'instrument', InstrumentViewSet)
router.register(r'fork', ForkViewSet)
router.register(r'session', SessionViewSet)

urlpatterns = [
    url(r'sign_up/vk/', VKAuthView.as_view(), name='sign_up_vk'),
    url(r'sign_up/fb/', FBAuthView.as_view(), name='sign_up_fb'),
    url(r'', include(router.urls))
]
