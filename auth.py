from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
import os

api_key_header = APIKeyHeader(name="X-API-Key")


async def get_api_key(x_api_key: str = Depends(api_key_header)):
    if x_api_key is None:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="API key not provided")
    return x_api_key


async def verify_api_key(api_key: str = Depends(get_api_key)):
    if api_key != os.getenv("X_API_KEY"):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API key")
    return api_key