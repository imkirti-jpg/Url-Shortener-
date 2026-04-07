from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Auth.service import decode_token
import jwt


oauth_schema = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth_schema)) -> str:
    try:
        payload = decode_token(credentials.credentials)
        return payload["sub"]  # email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
