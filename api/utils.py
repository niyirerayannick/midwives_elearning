import random
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from .models import HealthProviderUser, OneTimePassword
from twilio.rest import Client

def send_otp_to_email_and_sms(registration_number, request):
    """
    Generates and sends OTP to the user's email and phone for password reset.
    """
    subject = "One-Time Passcode for Verification"
    otp = random.randint(100000, 999999)  # Generate a 6-digit OTP
    current_site = get_current_site(request).domain

    try:
        user = HealthProviderUser.objects.get(registration_number=registration_number)
    except HealthProviderUser.DoesNotExist:
        return "User not found."

    # Create or update OTP entry for the user
    otp_obj, created = OneTimePassword.objects.update_or_create(user=user, defaults={'otp': otp})

    # Email message
    email_body = f"Hi {user.first_name},\n\n" \
                 f"Your one-time passcode (OTP) is: {otp}\n\n" \
                 "If you did not request this, please ignore this email."

    from_email = settings.EMAIL_HOST_USER
    email_message = EmailMessage(subject, email_body, from_email, [user.email])
    email_message.send()

    # Send OTP via SMS
    send_sms(user.telephone, otp)

    return "OTP sent successfully to email and SMS."

def send_sms(telephone, otp):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f"Your OTP is: {otp}",
        from_=settings.TWILIO_PHONE_NUMBER,  # Your Twilio number
        to=telephone
    )
    return message.sid
