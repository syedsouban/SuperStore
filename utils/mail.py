import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

def send_mail(receiver_email,subject,is_html_message,message_str):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = "sender_email"
    message["To"] = receiver_email

    part = MIMEText(message_str, "html" if is_html_message else "plain")
    
    # The email client will try to render the last part first
    message.attach(part)
    
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "superstoredummy@gmail.com"  # Enter your address
    password = "s3ndm@!l890"

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

def send_verification_mail(server_url,receiver_email,token):
    if not server_url:
        logging.exception("Resend verification mail for %s(Unable to fetch server host)"%receiver_email)
    else:
        verification_mail_message = """You have registered with SuperStore but you need to confirm your mail to access all features.<br>Click the following link to verify you email account %s/verify_email/%s/%s """%(server_url,receiver_email,token)
        send_mail(receiver_email,"Verify your SuperStore Account",True,verification_mail_message)

def send_password_reset_mail(server_url,receiver_email,token):
    if not server_url:
        logging.exception("Resend verification mail for %s(Unable to fetch server host)"%receiver_email)
    else:
        verification_mail_message = """Click the following link to reset your password for your SuperStore account %s/reset_password/%s/%s """%(server_url,receiver_email,token)
        send_mail(receiver_email,"Reset your SuperStore Account Password",True,verification_mail_message)
