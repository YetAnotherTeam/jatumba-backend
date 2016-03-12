import binascii
import os
import time


def generate_session_params(user):
    return {
        'access_token': binascii.hexlify(os.urandom(10)).decode('utf-8'),
        'refresh_token': binascii.hexlify(os.urandom(10)).decode('utf-8'),
        'time': int(time.time()),
        'user': user
    }
