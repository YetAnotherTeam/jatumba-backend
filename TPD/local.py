from TPD.develop import *  # noqa

MIDDLEWARE_CLASSES.remove('rollbar.contrib.django.middleware.RollbarNotifierMiddleware')
