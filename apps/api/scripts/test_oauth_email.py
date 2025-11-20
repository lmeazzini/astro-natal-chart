#!/usr/bin/env python3
"""
Test script for OAuth2 email sending.

Usage:
    uv run python scripts/test_oauth_email.py
"""

import asyncio
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings  # noqa: E402
from app.services.email import EmailService  # noqa: E402


async def test_oauth_email():
    """Test OAuth2 email sending."""
    print("🔍 Testing OAuth2 email configuration...\n")

    email_service = EmailService()

    # Check configuration
    if not email_service.oauth_enabled and not email_service.smtp_enabled:
        print("❌ Email not configured!")
        print("\nNeither OAuth2 nor SMTP is configured.")
        print("Please configure one of the following in your .env file:\n")
        print("Option 1: OAuth2 (Recommended)")
        print("  GMAIL_CLIENT_ID=...")
        print("  GMAIL_CLIENT_SECRET=...")
        print("  GMAIL_REFRESH_TOKEN=...")
        print("  SMTP_FROM_EMAIL=...\n")
        print("Option 2: SMTP (Fallback)")
        print("  SMTP_HOST=smtp.gmail.com")
        print("  SMTP_PORT=587")
        print("  SMTP_USER=...")
        print("  SMTP_PASSWORD=...")
        print("  SMTP_FROM_EMAIL=...")
        print("  SMTP_USE_TLS=True")
        return False

    if email_service.oauth_enabled:
        print("✅ OAuth2 configured")
        print(f"   Client ID: {settings.GMAIL_CLIENT_ID}")
        print(f"   From Email: {settings.SMTP_FROM_EMAIL}\n")
    elif email_service.smtp_enabled:
        print("✅ SMTP configured")
        print(f"   Host: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
        print(f"   User: {settings.SMTP_USER}")
        print(f"   From: {settings.SMTP_FROM_EMAIL}\n")

    # Get recipient email
    if email_service.oauth_enabled:
        # For OAuth2, send to the configured FROM_EMAIL
        to_email = settings.SMTP_FROM_EMAIL
    elif email_service.smtp_enabled:
        # For SMTP, send to SMTP_USER
        to_email = settings.SMTP_USER
    else:
        to_email = "test@example.com"

    print(f"📧 Sending test email to {to_email}...")

    # Send test email
    success = await email_service.send_email(
        to_email=to_email,
        subject="OAuth2 Test - Astro App",
        html_body="""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="background-color: #f4f4f4; border-radius: 10px; padding: 30px;">
                <h1 style="color: #4F46E5;">🎉 Success!</h1>
                <p>OAuth2 email configuration is working correctly!</p>
                <h3>Configuration Details:</h3>
                <ul>
                    <li><strong>Method:</strong> {}</li>
                    <li><strong>From:</strong> {}</li>
                    <li><strong>To:</strong> {}</li>
                </ul>
                <p style="color: #666; font-size: 14px; margin-top: 30px;">
                    This is an automated test email from Astro App.
                </p>
            </div>
        </body>
        </html>
        """.format(
            "OAuth2 (Gmail API)" if email_service.oauth_enabled else "SMTP",
            settings.SMTP_FROM_EMAIL,
            to_email
        ),
        text_body=f"""
        OAuth2 Test - Astro App

        Success! Email configuration is working correctly!

        Method: {"OAuth2 (Gmail API)" if email_service.oauth_enabled else "SMTP"}
        From: {settings.SMTP_FROM_EMAIL}
        To: {to_email}

        This is an automated test email from Astro App.
        """,
    )

    if success:
        print("\n✅ Email sent successfully!")
        print(f"\nCheck your inbox at {to_email}")
        if email_service.oauth_enabled:
            print("\n💡 OAuth2 is working! You can now use email features in the app.")
        return True
    else:
        print("\n❌ Failed to send email")
        print("\nCheck the logs above for error details.")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_oauth_email())
    sys.exit(0 if result else 1)
