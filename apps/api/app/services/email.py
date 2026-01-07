"""
Email service for sending transactional emails.
"""

import asyncio
import base64
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import partial
from pathlib import Path

import aiosmtplib
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build  # type: ignore[import-untyped]
from googleapiclient.errors import HttpError  # type: ignore[import-untyped]
from jinja2 import Environment, FileSystemLoader
from loguru import logger

from app.core.config import settings
from app.core.i18n.messages import EmailMessages
from app.core.i18n.translator import translate


class EmailService:
    """Serviço para envio de emails transacionais."""

    def __init__(self) -> None:
        """Inicializa o serviço de email."""
        # Check if OAuth2 is configured
        self.oauth_enabled = bool(
            settings.GMAIL_CLIENT_ID
            and settings.GMAIL_CLIENT_SECRET
            and settings.GMAIL_REFRESH_TOKEN
        )

        # Check if SMTP is configured (fallback)
        self.smtp_enabled = bool(
            settings.SMTP_HOST
            and settings.SMTP_PORT
            and settings.SMTP_USER
            and settings.SMTP_PASSWORD
        )

        if self.oauth_enabled:
            logger.info("EmailService: Using OAuth2 (Gmail API)")
            self._init_oauth()
        elif self.smtp_enabled:
            logger.info("EmailService: Using SMTP")
        else:
            logger.warning(
                "Email não configurado. Emails serão apenas logados (modo desenvolvimento)."
            )

        # Setup Jinja2 for email templates
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))

    def _init_oauth(self) -> None:
        """Initialize OAuth2 credentials."""
        self.credentials = Credentials(
            token=None,
            refresh_token=settings.GMAIL_REFRESH_TOKEN,
            token_uri=settings.GMAIL_TOKEN_URI,
            client_id=settings.GMAIL_CLIENT_ID,
            client_secret=settings.GMAIL_CLIENT_SECRET,
            scopes=["https://www.googleapis.com/auth/gmail.send"],
        )

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str | None = None,
    ) -> bool:
        """
        Envia email usando o método configurado (OAuth2 ou SMTP).

        Args:
            to_email: Email do destinatário
            subject: Assunto do email
            html_body: Corpo do email em HTML
            text_body: Corpo do email em texto plano (opcional)

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        # Dev mode: just log
        if not self.oauth_enabled and not self.smtp_enabled:
            logger.info(
                f"[DEV MODE] Email para {to_email}\n"
                f"Assunto: {subject}\n"
                f"Corpo:\n{text_body or html_body[:200]}..."
            )
            return True

        # Use OAuth2 if available
        if self.oauth_enabled:
            return await self.send_email_oauth(to_email, subject, html_body, text_body)

        # Fallback to SMTP
        return await self.send_email_smtp(to_email, subject, html_body, text_body)

    async def send_email_oauth(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str | None = None,
    ) -> bool:
        """
        Envia email usando OAuth2 (Gmail API) de forma assíncrona.

        Usa run_in_executor() para evitar bloqueio do event loop durante
        operações síncronas de I/O (token refresh, Gmail API calls).

        Args:
            to_email: Email do destinatário
            subject: Assunto do email
            html_body: Corpo do email em HTML
            text_body: Corpo do email em texto plano (opcional)

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            loop = asyncio.get_event_loop()

            # 1. Refresh token if needed (async via executor)
            if not self.credentials.valid:
                await loop.run_in_executor(
                    None,  # Uses default ThreadPoolExecutor
                    self.credentials.refresh,
                    Request(),
                )

            # 2. Build Gmail service (async via executor)
            service = await loop.run_in_executor(
                None, partial(build, "gmail", "v1", credentials=self.credentials)
            )

            # 3. Create message (sync, but fast - no I/O)
            message = MIMEMultipart("alternative")
            message["From"] = settings.SMTP_FROM_EMAIL
            message["To"] = to_email
            message["Subject"] = subject

            # Add text and HTML parts
            if text_body:
                message.attach(MIMEText(text_body, "plain"))
            message.attach(MIMEText(html_body, "html"))

            # Encode message
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # 4. Send email (async via executor)
            send_func = partial(
                service.users().messages().send(userId="me", body={"raw": raw}).execute
            )
            await loop.run_in_executor(None, send_func)

            logger.info(f"Email enviado com sucesso via OAuth2 para {to_email}")
            return True

        except HttpError as e:
            logger.error(f"Gmail API error ao enviar email para {to_email}: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro ao enviar email via OAuth2 para {to_email}: {e}")
            return False

    async def send_email_smtp(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str | None = None,
    ) -> bool:
        """
        Envia email usando SMTP (método legado).

        Args:
            to_email: Email do destinatário
            subject: Assunto do email
            html_body: Corpo do email em HTML
            text_body: Corpo do email em texto plano (opcional)

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            # Criar mensagem
            message = MIMEMultipart("alternative")
            message["From"] = settings.SMTP_FROM_EMAIL
            message["To"] = to_email
            message["Subject"] = subject

            # Adicionar corpo texto plano
            if text_body:
                part1 = MIMEText(text_body, "plain")
                message.attach(part1)

            # Adicionar corpo HTML
            part2 = MIMEText(html_body, "html")
            message.attach(part2)

            # Enviar via SMTP
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                use_tls=settings.SMTP_USE_TLS,
            )

            logger.info(f"Email enviado com sucesso via SMTP para {to_email}")
            return True

        except Exception as e:
            logger.error(f"Erro ao enviar email via SMTP para {to_email}: {e}")
            return False

    async def send_password_reset_email(
        self,
        to_email: str,
        user_name: str,
        reset_url: str,
        expires_hours: int = 1,
        locale: str | None = None,
    ) -> bool:
        """
        Envia email de recuperação de senha.

        Args:
            to_email: Email do destinatário
            user_name: Nome do usuário
            reset_url: URL para resetar senha
            expires_hours: Horas até expiração do link
            locale: User locale for translations (e.g., 'pt-BR', 'en-US')

        Returns:
            True se enviado com sucesso
        """
        # Get translations
        subject = translate(EmailMessages.PASSWORD_RESET_SUBJECT, locale=locale)
        title = translate(EmailMessages.PASSWORD_RESET_TITLE, locale=locale)
        greeting = translate(EmailMessages.GREETING, locale=locale, name=user_name)
        intro = translate(EmailMessages.PASSWORD_RESET_INTRO, locale=locale)
        action = translate(EmailMessages.PASSWORD_RESET_ACTION, locale=locale)
        button_text = translate(EmailMessages.PASSWORD_RESET_BUTTON, locale=locale)
        expiry = translate(
            EmailMessages.PASSWORD_RESET_EXPIRY, locale=locale, hours=str(expires_hours)
        )
        ignore = translate(EmailMessages.PASSWORD_RESET_IGNORE, locale=locale)
        button_help = translate(EmailMessages.BUTTON_NOT_WORKING, locale=locale)
        copyright_text = translate(
            EmailMessages.FOOTER_COPYRIGHT, locale=locale, year=str(datetime.now().year)
        )

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; color: #1a2035; background-color: #faf9f6; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 24px rgba(26, 31, 54, 0.08);">
                <div style="background: #1a1f36; padding: 40px 24px; text-align: center;">
                    <h1 style="font-family: 'Playfair Display', Georgia, serif; color: #d4a84b; font-size: 24px; margin: 0;">{title}</h1>
                </div>
                <div style="padding: 40px 32px;">
                    <p style="font-size: 15px; color: #606780; margin-bottom: 16px;">{greeting}</p>

                    <p style="font-size: 15px; color: #606780; margin-bottom: 16px;">{intro}</p>

                    <p style="font-size: 15px; color: #606780; margin-bottom: 24px;">{action}</p>

                    <div style="text-align: center; margin: 32px 0;">
                        <a href="{reset_url}"
                           style="background-color: #d4a84b; color: #1a1f36; padding: 16px 32px; text-decoration: none; border-radius: 50px; display: inline-block; font-weight: 600; font-size: 15px; box-shadow: 0 4px 16px rgba(212, 168, 75, 0.3);">
                            {button_text}
                        </a>
                    </div>

                    <p style="color: #606780; font-size: 14px; background: #faf9f6; padding: 16px; border-radius: 8px; border: 1px solid #e5e7eb;">
                        <strong style="color: #1a1f36;">⏰</strong> {expiry}
                    </p>

                    <p style="color: #606780; font-size: 14px; margin-top: 16px;">
                        {ignore}
                    </p>

                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 28px 0;">

                    <p style="color: #606780; font-size: 12px;">
                        {button_help}<br>
                        <a href="{reset_url}" style="color: #d4a84b; word-break: break-all;">{reset_url}</a>
                    </p>
                </div>
                <div style="background: #1a1f36; padding: 24px; text-align: center;">
                    <p style="color: rgba(255, 255, 255, 0.6); font-size: 12px; margin: 0;">
                        {copyright_text}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        {title}

        {greeting}

        {intro}

        {action}
        {reset_url}

        {expiry}

        {ignore}

        ---
        {copyright_text}
        """

        return await self.send_email(to_email, subject, html_body, text_body)

    async def send_password_changed_email(
        self,
        to_email: str,
        user_name: str,
        locale: str | None = None,
    ) -> bool:
        """
        Envia email de confirmação de senha alterada.

        Args:
            to_email: Email do destinatário
            user_name: Nome do usuário
            locale: User locale for translations (e.g., 'pt-BR', 'en-US')

        Returns:
            True se enviado com sucesso
        """
        # Get translations
        subject = translate(EmailMessages.PASSWORD_CHANGED_SUBJECT, locale=locale)
        title = translate(EmailMessages.PASSWORD_CHANGED_TITLE, locale=locale)
        greeting = translate(EmailMessages.GREETING, locale=locale, name=user_name)
        success_msg = translate(EmailMessages.PASSWORD_CHANGED_SUCCESS, locale=locale)
        warning = translate(EmailMessages.PASSWORD_CHANGED_WARNING, locale=locale)
        login_button = translate(EmailMessages.PASSWORD_CHANGED_LOGIN, locale=locale)
        copyright_text = translate(
            EmailMessages.FOOTER_COPYRIGHT, locale=locale, year=str(datetime.now().year)
        )

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; color: #1a2035; background-color: #faf9f6; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 24px rgba(26, 31, 54, 0.08);">
                <div style="background: #1a1f36; padding: 40px 24px; text-align: center;">
                    <h1 style="font-family: 'Playfair Display', Georgia, serif; color: #d4a84b; font-size: 24px; margin: 0;">{title}</h1>
                </div>
                <div style="padding: 40px 32px;">
                    <div style="text-align: center; margin-bottom: 24px;">
                        <div style="width: 64px; height: 64px; background: #d4a84b; border-radius: 50%; margin: 0 auto; display: flex; align-items: center; justify-content: center;">
                            <span style="color: #1a1f36; font-size: 32px;">&#10003;</span>
                        </div>
                    </div>

                    <p style="font-size: 15px; color: #606780; margin-bottom: 16px;">{greeting}</p>

                    <p style="font-size: 15px; color: #606780; margin-bottom: 16px;">{success_msg}</p>

                    <p style="color: #606780; font-size: 14px; background: #faf9f6; padding: 16px; border-radius: 8px; border: 1px solid #e5e7eb;">
                        {warning}
                    </p>

                    <div style="text-align: center; margin: 32px 0;">
                        <a href="{settings.FRONTEND_URL}/login"
                           style="background-color: #d4a84b; color: #1a1f36; padding: 16px 32px; text-decoration: none; border-radius: 50px; display: inline-block; font-weight: 600; font-size: 15px; box-shadow: 0 4px 16px rgba(212, 168, 75, 0.3);">
                            {login_button}
                        </a>
                    </div>
                </div>
                <div style="background: #1a1f36; padding: 24px; text-align: center;">
                    <p style="color: rgba(255, 255, 255, 0.6); font-size: 12px; margin: 0;">
                        {copyright_text}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        {title}

        {greeting}

        {success_msg}

        {warning}

        {settings.FRONTEND_URL}/login

        ---
        {copyright_text}
        """

        return await self.send_email(to_email, subject, html_body, text_body)

    async def send_verification_email(
        self,
        to_email: str,
        user_name: str,
        verification_url: str,
        locale: str | None = None,
    ) -> bool:
        """
        Envia email de verificação de conta.

        Args:
            to_email: Email do destinatário
            user_name: Nome do usuário
            verification_url: URL para verificar email (com token)
            locale: User locale for translations (e.g., 'pt-BR', 'en-US')

        Returns:
            True se enviado com sucesso
        """
        # Get translations
        subject = translate(EmailMessages.VERIFY_EMAIL_SUBJECT, locale=locale)
        title = translate(EmailMessages.VERIFY_EMAIL_TITLE, locale=locale)
        greeting = translate(EmailMessages.GREETING, locale=locale, name=user_name)
        intro = translate(EmailMessages.VERIFY_EMAIL_INTRO, locale=locale)
        action = translate(EmailMessages.VERIFY_EMAIL_ACTION, locale=locale)
        button_text = translate(EmailMessages.VERIFY_EMAIL_BUTTON, locale=locale)
        expiry = translate(EmailMessages.VERIFY_EMAIL_EXPIRY, locale=locale)
        ignore = translate(EmailMessages.VERIFY_EMAIL_IGNORE, locale=locale)
        button_help = translate(EmailMessages.BUTTON_NOT_WORKING, locale=locale)
        copyright_text = translate(
            EmailMessages.FOOTER_COPYRIGHT, locale=locale, year=str(datetime.now().year)
        )

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; color: #1a2035; background-color: #faf9f6; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 24px rgba(26, 31, 54, 0.08);">
                <div style="background: #1a1f36; padding: 40px 24px; text-align: center;">
                    <h1 style="font-family: 'Playfair Display', Georgia, serif; color: #d4a84b; font-size: 24px; margin: 0;">{title}</h1>
                </div>
                <div style="padding: 40px 32px;">
                    <p style="font-size: 15px; color: #606780; margin-bottom: 16px;">{greeting}</p>

                    <p style="font-size: 15px; color: #606780; margin-bottom: 16px;">{intro}</p>

                    <p style="font-size: 15px; color: #606780; margin-bottom: 24px;">{action}</p>

                    <div style="text-align: center; margin: 32px 0;">
                        <a href="{verification_url}"
                           style="background-color: #d4a84b; color: #1a1f36; padding: 16px 32px; text-decoration: none; border-radius: 50px; display: inline-block; font-weight: 600; font-size: 15px; box-shadow: 0 4px 16px rgba(212, 168, 75, 0.3);">
                            {button_text}
                        </a>
                    </div>

                    <p style="color: #606780; font-size: 14px; background: #faf9f6; padding: 16px; border-radius: 8px; border: 1px solid #e5e7eb;">
                        <strong style="color: #1a1f36;">⏰</strong> {expiry}
                    </p>

                    <p style="color: #606780; font-size: 14px; margin-top: 16px;">
                        {ignore}
                    </p>

                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 28px 0;">

                    <p style="color: #606780; font-size: 12px;">
                        {button_help}<br>
                        <a href="{verification_url}" style="color: #d4a84b; word-break: break-all;">{verification_url}</a>
                    </p>
                </div>
                <div style="background: #1a1f36; padding: 24px; text-align: center;">
                    <p style="color: rgba(255, 255, 255, 0.6); font-size: 12px; margin: 0;">
                        {copyright_text}<br>
                        <a href="{settings.FRONTEND_URL}" style="color: #d4a84b;">realastrology.ai</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        {title}

        {greeting}

        {intro}

        {action}
        {verification_url}

        {expiry}

        {ignore}

        ---
        {copyright_text}
        realastrology.ai
        """

        return await self.send_email(to_email, subject, html_body, text_body)

    async def send_welcome_email(
        self,
        to_email: str,
        user_name: str,
    ) -> bool:
        """
        Envia email de boas-vindas após confirmação de email.

        Args:
            to_email: Email do destinatário
            user_name: Nome do usuário

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        # Prepare template context
        context = {
            "user_name": user_name or "Usuário",
            "user_email": to_email,
            "dashboard_url": settings.FRONTEND_URL,
            "settings_url": f"{settings.FRONTEND_URL}/settings",
            "support_email": getattr(settings, "SUPPORT_EMAIL", "support@realastrology.ai"),
            "current_year": datetime.now().year,
        }

        # Render templates
        html_template = self.jinja_env.get_template("welcome.html")
        text_template = self.jinja_env.get_template("welcome.txt")

        html_body = html_template.render(**context)
        text_body = text_template.render(**context)

        # Send email
        subject = "✨ Bem-vindo ao Real Astrology!"

        success = await self.send_email(
            to_email=to_email,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
        )

        if success:
            logger.info("Welcome email sent successfully", extra={"to_email": to_email})
        else:
            logger.error("Failed to send welcome email", extra={"to_email": to_email})

        return success
