"""
Security utilities for authentication and encryption
"""
from datetime import datetime, timedelta
from typing import Optional, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
import hashlib
import secrets
from cryptography.fernet import Fernet
import base64

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(subject: Any, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        subject: Token subject (usually user ID)
        expires_delta: Token expiration time
    
    Returns:
        Encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Any) -> str:
    """
    Create JWT refresh token
    
    Args:
        subject: Token subject (usually user ID)
    
    Returns:
        Encoded JWT token
    """
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    Verify JWT token and return subject
    
    Args:
        token: JWT token to verify
    
    Returns:
        Token subject (user ID) if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


def get_password_hash(password: str) -> str:
    """
    Hash password using bcrypt
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
    
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def hash_keyword(keyword: str) -> str:
    """
    Hash trigger keyword using SHA-256
    
    Args:
        keyword: Plain text keyword
    
    Returns:
        Hashed keyword
    """
    return hashlib.sha256(keyword.encode()).hexdigest()


def verify_keyword(plain_keyword: str, hashed_keyword: str) -> bool:
    """
    Verify keyword against hash
    
    Args:
        plain_keyword: Plain text keyword
        hashed_keyword: Hashed keyword
    
    Returns:
        True if keyword matches, False otherwise
    """
    return hash_keyword(plain_keyword) == hashed_keyword


def generate_share_token() -> str:
    """
    Generate secure random share token
    
    Returns:
        Random token string
    """
    return secrets.token_urlsafe(32)


def encrypt_data(data: str) -> str:
    """
    Encrypt sensitive data using Fernet
    
    Args:
        data: Plain text data
    
    Returns:
        Encrypted data (base64 encoded)
    """
    # Create Fernet instance with encryption key
    key = base64.urlsafe_b64encode(settings.ENCRYPTION_KEY.encode()[:32].ljust(32, b'\0'))
    f = Fernet(key)
    encrypted = f.encrypt(data.encode())
    return encrypted.decode()


def decrypt_data(encrypted_data: str) -> str:
    """
    Decrypt sensitive data using Fernet
    
    Args:
        encrypted_data: Encrypted data (base64 encoded)
    
    Returns:
        Decrypted plain text data
    """
    # Create Fernet instance with encryption key
    key = base64.urlsafe_b64encode(settings.ENCRYPTION_KEY.encode()[:32].ljust(32, b'\0'))
    f = Fernet(key)
    decrypted = f.decrypt(encrypted_data.encode())
    return decrypted.decode()

