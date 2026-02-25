from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            app.logger.error(f'Failed to send email: {str(e)}')

def send_email(subject, sender, recipients, text_body, html_body=None):
    """
    Sends an email message asynchronously to avoid blocking the request.
    """
    if not isinstance(recipients, list):
        recipients = [recipients]
        
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    if html_body:
        msg.html = html_body
        
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()
