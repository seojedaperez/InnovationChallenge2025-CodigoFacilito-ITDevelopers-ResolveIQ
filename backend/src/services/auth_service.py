import os
from typing import Optional
from fastapi import HTTPException, Security, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
import requests
import logging

logger = logging.getLogger(__name__)

# Configuration
TENANT_ID = os.getenv("AZURE_AD_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_AD_CLIENT_ID")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
JWKS_URL = f"{AUTHORITY}/discovery/v2.0/keys"
ISSUER = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0"

security = HTTPBearer()

class AuthService:
    _jwks = None

    @classmethod
    def get_jwks(cls, jwks_url: str):
        if not cls._jwks:
            try:
                response = requests.get(jwks_url)
                response.raise_for_status()
                cls._jwks = response.json()
            except Exception as e:
                logger.error(f"Failed to fetch JWKS: {e}")
                raise HTTPException(status_code=500, detail="Internal authentication error")
        return cls._jwks

    @classmethod
    def validate_token(cls, token: str) -> dict:
        tenant_id = os.getenv("AZURE_AD_TENANT_ID")
        client_id = os.getenv("AZURE_AD_CLIENT_ID")
        
        if not tenant_id or not client_id:
            # If auth is not configured, skip validation (DEV ONLY)
            # In production, this should raise an error
            logger.warning("Azure AD not configured (env vars missing). Skipping token validation.")
            return {"sub": "dev-user", "name": "Dev User", "email": "dev@local"}

        authority = f"https://login.microsoftonline.com/{tenant_id}"
        issuer = f"https://login.microsoftonline.com/{tenant_id}/v2.0"
        
        # Fetch JWKS if needed (using the authority)
        # Note: We might need to update JWKS_URL dynamically if tenant changes, 
        # but for now we assume single tenant or we need to refactor get_jwks.
        # For simplicity, let's assume JWKS_URL is also dynamic or we just use the global one 
        # if it was set correctly, but since we are fixing import time issues:
        jwks_url = f"{authority}/discovery/v2.0/keys"

        jwks = cls.get_jwks(jwks_url)
        
        try:
            # Get the key id from the header
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
                    break
            
            if not rsa_key:
                raise HTTPException(status_code=401, detail="Invalid token header")

            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=client_id, # Verify the token is for this app
                issuer=issuer,      # Verify the token is from our tenant
                options={
                    "verify_signature": True,
                    "verify_aud": True,
                    "verify_iss": True,
                    "verify_exp": True,
                }
            )
            return payload

        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except JWTClaimsError as e:
            logger.error(f"Claims error: {e}")
            raise HTTPException(status_code=401, detail="Invalid token claims")
        except JWTError as e:
            logger.error(f"JWT Error: {e}")
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        except Exception as e:
            logger.error(f"Auth Error: {e}")
            raise HTTPException(status_code=401, detail="Authentication failed")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Dependency to validate the Bearer token and return the user payload.
    """
    token = credentials.credentials
    return AuthService.validate_token(token)
