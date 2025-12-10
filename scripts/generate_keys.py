"""
Key Generation Utility

This module provides functions to generate cryptographically secure API keys and secret keys.
"""

import secrets


def generate_api_key() -> str:
    """
    Generate a cryptographically secure API key.
    
    Returns:
        str: A 64-character hexadecimal string (32 bytes)
        
    Example:
        >>> api_key = generate_api_key()
        >>> print(api_key)
        183a1c70f7cdc71c1f044b60fc6609a9a1659f5d8bc6b20bc7eb14f17bd73c9
    """
    return secrets.token_hex(32)


def generate_secret_key() -> str:
    """
    Generate a cryptographically secure secret key.
    
    Returns:
        str: A 128-character hexadecimal string (64 bytes)
        
    Example:
        >>> secret_key = generate_secret_key()
        >>> print(secret_key)
        9d453dcc645ecd3d22cec61ee99d5ac42d8217f1ae3bddccb7309f9e35cdfb02...
    """
    return secrets.token_hex(64)


def generate_keys() -> dict:
    """
    Generate both an API key and a secret key.
    
    Returns:
        dict: Dictionary containing 'api_key' and 'secret_key'
        
    Example:
        >>> keys = generate_keys()
        >>> print(keys['api_key'])
        >>> print(keys['secret_key'])
    """
    return {
        'api_key': generate_api_key(),
        'secret_key': generate_secret_key()
    }


if __name__ == '__main__':
    # When run as a script, generate and display both keys
    print("=" * 80)
    print("CRYPTOGRAPHIC KEY GENERATOR")
    print("=" * 80)
    print()
    
    api_key = generate_api_key()
    secret_key = generate_secret_key()
    
    print("API Key (64 hex chars, 32 bytes):")
    print(api_key)
    print()
    
    print("Secret Key (128 hex chars, 64 bytes):")
    print(secret_key)
    print()
    
    print("=" * 80)
    print("IMPORTANT: Store these keys securely!")
    print("- Never commit them to version control")
    print("- Use environment variables or secure key management")
    print("=" * 80)

