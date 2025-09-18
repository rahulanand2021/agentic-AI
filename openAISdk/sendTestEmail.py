import sendgrid
import os
from dotenv import load_dotenv
from sendgrid.helpers.mail import Mail, Email, To, Content

def loadAPIKeys():
    load_dotenv(override=True)

def sendTestEmail():
    sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
    from_email = Email("rahulanand2006@gmail.com")  # Change to your verified sender
    to_email = To("rahulanand2005@gmail.com")  # Change to your recipient
    content = Content("text/plain", "This is an important test email")
    mail = Mail(from_email, to_email, "Test email", content).get()
    response = sg.client.mail.send.post(request_body=mail)
    print(response.status_code)

if __name__ == "__main__":
    loadAPIKeys()
    sendTestEmail()