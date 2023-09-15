import jwt

from fastapi import Request


def get_userid_from_request(request: Request):
    """
    Extract the userid from the token
    :param request: Fastapi Request
    :return: str user id
    """
    _, token = request.headers["Authorization"].split(" ")
    return jwt.decode(token, options={"verify_signature": False})["sub"]


