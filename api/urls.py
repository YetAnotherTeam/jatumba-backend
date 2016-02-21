from django.conf.urls import url, include
from api.views import *


urlpatterns = [
    url(r'^hello/', HelloView.as_view()),
    url(r'^sign_up/', SignUpView.as_view()),
]
