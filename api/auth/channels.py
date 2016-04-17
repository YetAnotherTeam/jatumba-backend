import functools

from channels.handler import AsgiRequest
from django.contrib.auth.models import AnonymousUser

from api.models import Session


def token_auth(func):
    @functools.wraps(func)
    def inner(message, *args, **kwargs):
        # Make sure there's NOT a access_token already
        if hasattr(message, "token_session"):
            return func(message, *args, **kwargs)
        try:
            # We want to parse the WebSocket (or similar HTTP-lite) message
            # to get cookies and GET, but we need to add in a few things that
            # might not have been there.
            if "method" not in message.content:
                message.content['method'] = "FAKE"
            request = AsgiRequest(message)
        except Exception as e:
            raise ValueError(
                "Cannot parse HTTP message - are you sure this is a token consumer? %s" % e)
        # Make sure there's a session key
        access_token = request.GET.get("access_token", None)
        if access_token is None:
            access_token = request.COOKIES.get("access_token", None)
        # Make a session storage
        if access_token:
            session = Session.objects.filter(access_token=access_token).first()
        else:
            session = None
        message.token_session = session
        # Run the consumer
        result = func(message, *args, **kwargs)
        return result

    return inner


def token_session_user(func):
    """
    Wraps a HTTP or WebSocket consumer (or any consumer of messages
    that provides a "COOKIES" attribute) to provide both a "session"
    attribute and a "user" attibute, like AuthMiddleware does.

    This runs http_session() to get a session to hook auth off of.
    If the user does not have a session cookie set, both "session"
    and "user" will be None.
    """

    @token_auth
    @functools.wraps(func)
    def inner(message, *args, **kwargs):
        # If we didn't get a session, then we don't get a user
        if not hasattr(message, "token_session"):
            raise ValueError("Did not see a token session to get auth from")
        if message.token_session is None:
            message.user = AnonymousUser()
        else:
            message.user = message.token_session.user
        # Run the consumer
        return func(message, *args, **kwargs)
    return inner
