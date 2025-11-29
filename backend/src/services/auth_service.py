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
    def get_jwks(cls):
        if not cls._jwks:
            try:
                response = requests.get(JWKS_URL)
                response.raise_for_status()
                cls._jwks = response.json()
            except Exception as e:
                logger.error(f"Failed to fetch JWKS: {e}")
                raise HTTPException(status_code=500, detail="Internal authentication error")
        return cls._jwks

    @classmethod
    def validate_token(cls, token: str) -> dict:
        if not TENANT_ID or not CLIENT_ID:
            # If auth is not configured, skip validation (DEV ONLY)
            # In production, this should raise an error
            logger.warning("Azure AD not configured. Skipping token validation.")
            return {"sub": "dev-user", "name": "Dev User", "email": "dev@local"}

        jwks = cls.get_jwks()
        
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
                audience=CLIENT_ID, # Verify the token is for this app
                issuer=ISSUER,      # Verify the token is from our tenant
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
