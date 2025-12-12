from mailersend import MailerSendClient, EmailBuilder
import os
from dotenv import load_dotenv

def sendEmailUsingMailerSend(body: str):
    load_dotenv(override=True)
    api_key = os.getenv("MAILERSEND_API_KEY")
    
    if not api_key:
        error_msg = "Error: MAILERSEND_API_KEY environment variable is not set. Please check your .env file."
        print(error_msg)
        return error_msg

    # Initialize the MailerSend client
    client = MailerSendClient(api_key=api_key)

    # Build the email using the EmailBuilder
    email = (EmailBuilder()
        .from_email("MS_rEYZQ3@test-y7zpl98918o45vx6.mlsender.net", "Rahul")  # Must be your verified domain/sender
        .to("rahulanand2005@gmail.com", "Recipient")
        .subject("Test email")
        .text(body)
        .build())

    # Send the email
    response = client.emails.send(email)
    print(response)
    return response

sendEmailUsingMailerSend("This is a test email")