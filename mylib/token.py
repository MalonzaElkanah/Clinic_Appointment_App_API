from django.conf import settings

import jwt
import datetime as dt


KEY = settings.SECRET_KEY


def encode(data, key=KEY, expiration_seconds=3600):
    """
    Generates the Token
    :param data, key, expiration_seconds=3600:
    :return: string
    """
    try:
        payload = {
            'exp': dt.datetime.now().astimezone() + dt.timedelta(
                seconds=expiration_seconds
            ),
            'iat': dt.datetime.now().astimezone(),
            'data': data
        }
        return jwt.encode(payload=payload, key=key, algorithm='HS256')
    except Exception as e:
        return e


def decode(token, key=KEY):
    """
    Decodes the token
    :param token, key:
    :return: integer|string
    """
    try:
        payload = jwt.decode(jwt=token, key=key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token expired.'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token.'}
