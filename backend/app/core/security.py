"""
Security and Authentication Utilities
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import boto3
from botocore.exceptions import ClientError

from app.config import settings
from app.core.logging import logger
from app.core.exceptions import AuthenticationException


security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


class CognitoTokenVerifier:
    """Verify Cognito JWT tokens"""
    
    def __init__(self):
        self.region = settings.COGNITO_REGION
        self.user_pool_id = settings.COGNITO_USER_POOL_ID
        self.client_id = settings.COGNITO_CLIENT_ID
        self.keys = None
    
    async def get_public_keys(self) -> Dict[str, Any]:
        """Fetch Cognito public keys for JWT verification"""
        if self.keys:
            return self.keys
        
        import httpx
        
        url = f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                self.keys = response.json()
                return self.keys
        except Exception as e:
            logger.error(f"Failed to fetch Cognito public keys: {e}")
            raise AuthenticationException("Unable to verify token")
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode Cognito JWT token"""
        try:
            # Get public keys
            keys = await self.get_public_keys()
            
            # Decode header to get key ID
            headers = jwt.get_unverified_headers(token)
            kid = headers['kid']
            
            # Find matching key
            key = next((k for k in keys['keys'] if k['kid'] == kid), None)
            if not key:
                raise AuthenticationException("Invalid token")
            
            # Verify and decode token
            payload = jwt.decode(
                token,
                key,
                algorithms=['RS256'],
                audience=self.client_id,
                options={"verify_exp": True}
            )
            
            return payload
            
        except JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            raise AuthenticationException("Invalid or expired token")
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise AuthenticationException()


# Create verifier instance
token_verifier = CognitoTokenVerifier()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user
    """
    token = credentials.credentials
    user_data = await token_verifier.verify_token(token)
    
    return {
        "user_id": user_data.get("sub"),
        "email": user_data.get("email"),
        "username": user_data.get("cognito:username"),
        "token_payload": user_data
    }


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(optional_security)
) -> Optional[Dict[str, Any]]:
    """
    Dependency to get current user if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except AuthenticationException:
        return None
