import smtplib
from email.mime.text import MIMEText
from threading import Thread

from securypi_app.models.app_config import AppConfig
from securypi_app.models.app_secrets import AppSecrets


def send_email(to_address, subject, body):
    """
    Send a plain-text email via SMTP.
    Silently skips if SMTP is not configured (smtp_host empty).
    On error logs to stdout.
    """
    config = AppConfig.get()
    email_cfg = config.email

    if not email_cfg.smtp_host:
        print("Email not configured: smtp_host is empty. Skipping.")
        return

    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = email_cfg.smtp_username
    msg["To"] = to_address

    try:
        with smtplib.SMTP(email_cfg.smtp_host, email_cfg.smtp_port) as server:
            if email_cfg.smtp_use_tls:
                server.starttls()
            if email_cfg.smtp_username:
                server.login(email_cfg.smtp_username, AppSecrets.get().smtp_password)
            server.sendmail(msg["From"], [to_address], msg.as_string())
    except Exception as e:
        print(f"Failed to send email to {to_address}: {e}")


def send_email_async(to_address, subject, body):
    """ Dispatch send_email in a background daemon thread. """
    t = Thread(target=send_email, args=(to_address, subject, body), daemon=True)
    t.start()
