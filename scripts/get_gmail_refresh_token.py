#!/usr/bin/env python3
"""
Script to obtain OAuth2 refresh token for Gmail API.
Run once to get the refresh token, then save it in .env

Usage:
    uv run python scripts/get_gmail_refresh_token.py path/to/credentials.json
"""

import json
import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

# Gmail send scope
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def get_refresh_token(credentials_file: str) -> None:
    """
    Obtain refresh token via OAuth2 flow.
    Opens browser for authorization.
    """
    cred_path = Path(credentials_file)

    if not cred_path.exists():
        print(f"❌ Credentials file not found: {credentials_file}")
        print("\nDownload it from Google Cloud Console:")
        print("APIs & Services > Credentials > OAuth 2.0 Client IDs > Download JSON")
        sys.exit(1)

    # Load credentials from JSON
    with open(credentials_file) as f:
        creds_data = json.load(f)

    # Check if it's "web" or "installed" type
    if 'web' in creds_data:
        client_type = 'web'
        client_id = creds_data['web']['client_id']
        client_secret = creds_data['web']['client_secret']
    elif 'installed' in creds_data:
        client_type = 'installed'
        client_id = creds_data['installed']['client_id']
        client_secret = creds_data['installed']['client_secret']
    else:
        print("❌ Invalid credentials format. Expected 'web' or 'installed' key.")
        sys.exit(1)

    print(f"🔐 Starting OAuth2 flow (client type: {client_type})...")
    print("A browser window will open for authorization.")
    print("Sign in with your Google Workspace account.\n")

    # Run OAuth2 flow
    flow = InstalledAppFlow.from_client_secrets_file(
        credentials_file,
        SCOPES
    )

    # This opens browser automatically
    # Use port 8090 for local server (8080 may be in use)
    creds = flow.run_local_server(port=8090)

    print("\n✅ OAuth2 tokens obtained successfully!")
    print("\n" + "="*70)
    print("Add these lines to your apps/api/.env file:")
    print("="*70)
    print(f"\nGMAIL_CLIENT_ID={client_id}")
    print(f"GMAIL_CLIENT_SECRET={client_secret}")
    print(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}")
    print("\n" + "="*70)
    print("\n⚠️  Keep these credentials secure! Never commit to Git.")
    print("\n💡 You can now delete the credentials JSON file for security.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/get_gmail_refresh_token.py <credentials.json>")
        print("\nExample:")
        print("  uv run python scripts/get_gmail_refresh_token.py gmail_credentials.json")
        sys.exit(1)

    credentials_file = sys.argv[1]
    get_refresh_token(credentials_file)
