from django.conf.urls import url, include
from api.views import *

urlpatterns = [
    url(r'^sign_up/vk/', VkAuth.as_view()),
    url(r'^sign_up/fb/', FbAuth.as_view()),
    url(r'^sign_up/', SignUpView.as_view()),
    url(r'^token/refresh/', RefreshToken.as_view()),
    url(r'^profile/(?P<username>\w+)/$', ProfileView.as_view())
]
