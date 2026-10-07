import base64
from email.message import EmailMessage
from google_auth.auth_helper import get_gmail_service
from google_auth.email_renderer import render_briefing_html

def send_email(
        service,
        recipients: list[str],
        subject: str,
        html_body: str
):
    message = EmailMessage()
    message["to"] = ", ".join(recipients)
    message["Subject"] = subject

    message.set_content(
        "Please view this email in an HTML-capable email client"
    )
    message.add_alternative(
        html_body,
        subtype="html"
    )
    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    body = {
        "raw": encoded_message
    }
    return (
        service
        .users()
        .messages()
        .send(
            userId="me",
            body=body
        )
        .execute()
    )

if __name__=="__main__":
    service = get_gmail_service()

    send_email(
        service=service,
        recipients=["your-email@gmail.com"],
        subject="Daily Briefing Test",
        html_body="""
            <h1>Daily Briefing</h1>
            <p>If you're reading this, the Gmail API works 🎉</p>
        """
    )