# built in imports
import os
import random
import aiosmtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

# custom imports
GMAIL_USER= os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD= os.getenv("GMAIL_APP_PASSWORD")

def generate_otp() -> str:
    return str(random.randint(100000, 999999))

async def send_otp(to_email: str, otp: str )-> None:
    message = EmailMessage()
    message["From"] = GMAIL_USER
    message["To"] = to_email
    message["Subject"] = "Your Snip.ly OTP Code"
    message.set_content(f"""
        Hello!

        Your OTP code is: {otp}

        This code will expire in 10 minutes.

        — Snip.ly Team
      """)

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        username=GMAIL_USER,
        password=GMAIL_APP_PASSWORD,
        start_tls=True,
    )