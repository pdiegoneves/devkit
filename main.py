# from log.logger import Logger

# log = Logger.get_logger()


# log.info("Teste Info")
# log.warning("Teste Warning")
# log.error("Teste Error")
# log.success("Teste Success")
# log.debug("Teste Debug")
# log.critical("Teste Critical")

from send_email.send_mail import EmailSender

# Configuração básica
sender = EmailSender(
    username="email@email.com",
    password="password",
)

# Envio simples
sender.send_email(
    subject="Teste de Email",
    body="Este é um email de teste enviado pelo Python.",
    to_emails=["destinatario@example.com"],
)

# Envio com HTML e anexos
sender.send_html_email(
    subject="Relatório Mensal",
    html_content="<h1>Relatório Mensal</h1><p>Segue em anexo o relatório completo.</p>",
    to_emails=["pdcassiano@gmail.com"],
    # cc_emails=["gerente@example.com"],
    # attachments=["./relatorio.pdf", "./dados.xlsx"],
)
