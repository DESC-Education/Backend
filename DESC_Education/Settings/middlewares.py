from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from channels.middleware import BaseMiddleware
from channels.auth import AuthMiddlewareStack
from django.db import close_old_connections
from urllib.parse import parse_qs
from jwt import decode as jwt_decode
from django.conf import settings
import json
from urllib.parse import parse_qs

@database_sync_to_async
def get_user(validated_token):
    User = get_user_model()
    try:
        user = User.objects.get(id=validated_token["user_id"])
        return user

    except User.DoesNotExist:
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        close_old_connections()

        token = next((i for i in scope["headers"] if i[0] == b'sec-websocket-protocol'), None)
        if token is None:
            scope["user"] = AnonymousUser()
        else:
            token = token[1].decode("utf-8")
            try:
                AccessToken(token)
            except (InvalidToken, TokenError) as e:
                print(str(e))
                await send({
                    'type': 'websocket.accept',
                })
                await send({
                    'type': 'websocket.close',
                    'code': 4001,
                    'reason': f'{str(e)}'
                })
                return
            else:
                decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user = await get_user(validated_token=decoded_data)
                scope["user"] = user
        return await super().__call__(scope, receive, send)


def JwtAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(AuthMiddlewareStack(inner))
