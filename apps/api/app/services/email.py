"""
Email service for sending transactional emails.
"""

import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build  # type: ignore[import-untyped]
from googleapiclient.errors import HttpError  # type: ignore[import-untyped]
from loguru import logger

from app.core.config import settings


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
        Envia email usando OAuth2 (Gmail API).

        Args:
            to_email: Email do destinatário
            subject: Assunto do email
            html_body: Corpo do email em HTML
            text_body: Corpo do email em texto plano (opcional)

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            # Refresh token if needed (synchronous, but fast)
            if not self.credentials.valid:
                self.credentials.refresh(Request())

            # Build Gmail service
            service = build('gmail', 'v1', credentials=self.credentials)

            # Create message
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

            # Send via Gmail API
            service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()

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
    ) -> bool:
        """
        Envia email de recuperação de senha.

        Args:
            to_email: Email do destinatário
            user_name: Nome do usuário
            reset_url: URL para resetar senha
            expires_hours: Horas até expiração do link

        Returns:
            True se enviado com sucesso
        """
        subject = "Recuperação de Senha - Astro App"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 20px;">
                <img src="{settings.FRONTEND_URL}/logo.png" alt="Astro" style="width: 80px; height: 80px;" />
            </div>
            <div style="background-color: #f4f4f4; border-radius: 10px; padding: 30px;">
                <h1 style="color: #4F46E5; margin-top: 0;">Recuperação de Senha</h1>

                <p>Olá, <strong>{user_name}</strong>!</p>

                <p>Recebemos uma solicitação para redefinir a senha da sua conta no Astro App.</p>

                <p>Se você fez essa solicitação, clique no botão abaixo para criar uma nova senha:</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}"
                       style="background-color: #4F46E5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                        Redefinir Senha
                    </a>
                </div>

                <p style="color: #666; font-size: 14px;">
                    <strong>Atenção:</strong> Este link expira em <strong>{expires_hours} hora(s)</strong>.
                </p>

                <p style="color: #666; font-size: 14px;">
                    Se você não solicitou a redefinição de senha, ignore este email. Sua senha permanecerá inalterada.
                </p>

                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

                <p style="color: #999; font-size: 12px;">
                    Se o botão não funcionar, copie e cole este link no seu navegador:<br>
                    <a href="{reset_url}" style="color: #4F46E5; word-break: break-all;">{reset_url}</a>
                </p>

                <p style="color: #999; font-size: 12px; margin-top: 30px;">
                    © 2025 Astro App. Todos os direitos reservados.
                </p>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Recuperação de Senha - Astro App

        Olá, {user_name}!

        Recebemos uma solicitação para redefinir a senha da sua conta.

        Para criar uma nova senha, acesse o link abaixo:
        {reset_url}

        Este link expira em {expires_hours} hora(s).

        Se você não solicitou a redefinição de senha, ignore este email.

        ---
        © 2025 Astro App
        """

        return await self.send_email(to_email, subject, html_body, text_body)

    async def send_password_changed_email(
        self,
        to_email: str,
        user_name: str,
    ) -> bool:
        """
        Envia email de confirmação de senha alterada.

        Args:
            to_email: Email do destinatário
            user_name: Nome do usuário

        Returns:
            True se enviado com sucesso
        """
        subject = "Senha Alterada com Sucesso - Astro App"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 20px;">
                <img src="{settings.FRONTEND_URL}/logo.png" alt="Astro" style="width: 80px; height: 80px;" />
            </div>
            <div style="background-color: #f4f4f4; border-radius: 10px; padding: 30px;">
                <h1 style="color: #10B981; margin-top: 0;">✓ Senha Alterada</h1>

                <p>Olá, <strong>{user_name}</strong>!</p>

                <p>Sua senha foi alterada com sucesso.</p>

                <p style="color: #666; font-size: 14px;">
                    Se você não fez essa alteração, entre em contato com nosso suporte imediatamente.
                </p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{settings.FRONTEND_URL}/login"
                       style="background-color: #10B981; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                        Fazer Login
                    </a>
                </div>

                <p style="color: #999; font-size: 12px; margin-top: 30px;">
                    © 2025 Astro App. Todos os direitos reservados.
                </p>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Senha Alterada com Sucesso - Astro App

        Olá, {user_name}!

        Sua senha foi alterada com sucesso.

        Se você não fez essa alteração, entre em contato com nosso suporte imediatamente.

        Acesse: {settings.FRONTEND_URL}/login

        ---
        © 2025 Astro App
        """

        return await self.send_email(to_email, subject, html_body, text_body)
