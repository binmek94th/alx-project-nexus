import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from celery import shared_task

from alx_project_nexus.settings import EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD


@shared_task
def send_email(subject, message_plain, message_html, recipient_list):
    for recipient in recipient_list:
        try:
            email_msg = MIMEMultipart("alternative")
            email_msg["Subject"] = subject
            email_msg["From"] = 'noreply@gmail.com'
            email_msg["To"] = recipient

            text_part = MIMEText(message_plain, "plain")
            html_part = MIMEText(message_html, "html")
            email_msg.attach(text_part)
            email_msg.attach(html_part)

            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(EMAIL_HOST_USER, recipient_list, email_msg.as_string())
            server.quit()

        except Exception as e:
            print(f"Failed to send email: {e}")
