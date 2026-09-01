from django.core.mail import EmailMessage  # Used to create and send emails
from hashlib import sha1  # Used to securely hash data (like tokens)
from datetime import timedelta  # To handle dates and times
from .models import ResetToken  # Our model to store password reset tokens
from django.urls import reverse  # To get URL from named paths
import secrets  # For generating secure random tokens
from django.utils import timezone


def generate_reset_url(user):
    """
    View to generate a password reset url.

    :param user: current user.
    :return: reverse a template with a password reset form with a reset token
    passed into it.
    """
    token = secrets.token_urlsafe(16)  # Generate a random secure token
    expiry = timezone.now() + timedelta(minutes=15)  # Token expires in 15 minutes

    hashed_token = sha1(token.encode()).hexdigest()  # Hash the token to store securely

    # Save this token and expiry time in the database linked to the user
    ResetToken.objects.create(user=user, token=hashed_token, expiry_date=expiry)

    # Return the URL path for the password reset page, including the token
    # This URL will be something like /grabsomore/reset_password/<token>/
    return reverse('grabsomore:password_reset_form', kwargs={'token': token})


def build_email(user, url):
    """
    View to generate a password reset email.

    :param user: current user.
    :param url: the password reset url
    :return: email object for password reset.
    """
    subject = 'Password Reset Request'  # Email subject line

    # Email message body, showing the user their reset link
    # The URL includes the reset token, so they can reset their password securely
    body = f'Hello {user.username},\n\nClick the link below to reset your password:\n\nhttp://localhost:8000{url}'

    # Create the email object, setting the recipient to the user's email address
    email = EmailMessage(subject, body, to=[user.email])

    return email  # Return the email object so it can be sent later
