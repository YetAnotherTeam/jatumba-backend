import binascii
import time
import os


def generate_identity():
    return {
        'access_token': binascii.hexlify(os.urandom(10)).decode('utf-8'),
        'refresh_token': binascii.hexlify(os.urandom(10)).decode('utf-8'),
        'last_update': int(time.time()),
        'expires': 3600,
    }