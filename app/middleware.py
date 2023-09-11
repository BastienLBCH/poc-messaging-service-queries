from fastapi import Request, HTTPException, FastAPI
from fastapi.responses import JSONResponse
from .settings import Settings

import jwt

settings = Settings()
app = FastAPI()


async def validate_token(token):
    keycloak_public_key = settings.keycloak_public_key
    keycloak_alg = settings.keycloak_alg
    key = '-----BEGIN PUBLIC KEY-----\n' + keycloak_public_key + '\n-----END PUBLIC KEY-----'

    payload = jwt.decode(
        token,
        key,
        algorithms=keycloak_alg,
        audience="account"
    )

    return payload


class ValidatingMiddleware:
    def __init__(self):
        pass

    async def __call__(self, request: Request, call_next):
        keycloak_public_key = settings.keycloak_public_key
        keycloak_alg = settings.keycloak_alg

        try:
            name, bearer = request.headers["Authorization"].split(" ")
            if name != "Bearer":
                raise Exception

            await validate_token(bearer)

        except Exception:
            return JSONResponse({'detail': "User is not correctly authentified"}, status_code=401)

        response = await call_next(request)
        return response








