from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .config import Settings

settings = Settings()
security = HTTPBearer()


def authenticate(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != settings.auth_token:
        raise HTTPException(status_code=403, detail="Unauthorized access")
