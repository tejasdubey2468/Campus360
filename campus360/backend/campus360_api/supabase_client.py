"""
Supabase client utility for storage and direct API access.
"""
import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')

_client: Client = None


def get_supabase_client() -> Client:
    """Returns a singleton Supabase client using the service role key."""
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return _client


def upload_to_supabase(bucket: str, file_path: str, file_data: bytes, content_type: str = 'application/octet-stream') -> str:
    """Upload a file to Supabase Storage and return the public URL."""
    client = get_supabase_client()
    client.storage.from_(bucket).upload(file_path, file_data, {'content-type': content_type})
    return client.storage.from_(bucket).get_public_url(file_path)


def delete_from_supabase(bucket: str, file_paths: list) -> None:
    """Delete files from Supabase Storage."""
    client = get_supabase_client()
    client.storage.from_(bucket).remove(file_paths)


def get_signed_url(bucket: str, file_path: str, expires_in: int = 3600) -> str:
    """Get a signed URL for private file access."""
    client = get_supabase_client()
    response = client.storage.from_(bucket).create_signed_url(file_path, expires_in)
    return response.get('signedURL', '')
