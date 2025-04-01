import os
import smtplib
import ssl
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

# Importando nosso logger pra usar no EmailSender
from log.logger import Logger


class EmailSender:
    """
    Classe para envio de e-mails com suporte a múltiplos destinatários,
    anexos e formatação HTML.
    """

    def __init__(
        self,
        smtp_server: str = "mail.maceioti.com.br",
        smtp_port: int = 587,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """
        Inicializa o EmailSender com as configurações do servidor SMTP.

        Args:
            smtp_server: Servidor SMTP (padrão: smtp.gmail.com)
            smtp_port: Porta do servidor (padrão: 587 para TLS)
            username: Email de login (se None, deve ser fornecido ao enviar)
            password: Senha ou token de app (se None, deve ser fornecido ao enviar)
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.logger = Logger.get_logger(__name__)

    def send_email(
        self,
        subject: str,
        body: str,
        to_emails: List[str],
        from_email: Optional[str] = None,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None,
        is_html: bool = False,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> bool:
        """
        Envia um email com os parâmetros fornecidos.

        Args:
            subject: Assunto do email
            body: Corpo do email
            to_emails: Lista de destinatários
            from_email: Email do remetente (se None, usa username)
            cc_emails: Lista de emails em cópia
            bcc_emails: Lista de emails em cópia oculta
            attachments: Lista de caminhos para arquivos anexos
            is_html: Se True, o corpo é formatado como HTML
            username: Email de login (sobrescreve o definido no __init__)
            password: Senha ou token (sobrescreve o definido no __init__)

        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        # Usar credenciais fornecidas ou as definidas no __init__
        username = username or self.username
        password = password or self.password

        if not username or not password:
            self.logger.error("Credenciais de email não fornecidas")
            return False

        # Usar from_email fornecido ou username como remetente
        from_email = from_email or username

        try:
            # Criar mensagem
            msg = MIMEMultipart()
            msg["From"] = from_email
            msg["To"] = ", ".join(to_emails)
            msg["Subject"] = subject

            # Adicionar CC se fornecido
            if cc_emails:
                msg["Cc"] = ", ".join(cc_emails)

            # Preparar lista completa de destinatários
            all_recipients = to_emails.copy()
            if cc_emails:
                all_recipients.extend(cc_emails)
            if bcc_emails:
                all_recipients.extend(bcc_emails)

            # Adicionar corpo do email
            if is_html:
                msg.attach(MIMEText(body, "html"))
            else:
                msg.attach(MIMEText(body, "plain"))

            # Adicionar anexos
            if attachments:
                for file_path in attachments:
                    try:
                        with open(file_path, "rb") as file:
                            part = MIMEApplication(
                                file.read(), Name=os.path.basename(file_path)
                            )
                            part["Content-Disposition"] = (
                                f'attachment; filename="{os.path.basename(file_path)}"'
                            )
                            msg.attach(part)
                    except Exception as e:
                        self.logger.error(f"Erro ao anexar arquivo {file_path}: {e}")

            # Conectar ao servidor SMTP
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(username, password)
                server.sendmail(from_email, all_recipients, msg.as_string())

            self.logger.success(
                f"Email enviado com sucesso para {len(all_recipients)} destinatário(s)"
            )
            return True

        except Exception as e:
            self.logger.error(f"Erro ao enviar email: {e}")
            return False

    def send_html_email(
        self, subject: str, html_content: str, to_emails: List[str], **kwargs
    ) -> bool:
        """
        Método auxiliar para enviar email HTML.
        Aceita os mesmos parâmetros de send_email, exceto body e is_html.
        """
        return self.send_email(
            subject=subject,
            body=html_content,
            to_emails=to_emails,
            is_html=True,
            **kwargs,
        )
