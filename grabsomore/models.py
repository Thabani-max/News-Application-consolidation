from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True, null=False, blank=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    ROLE_CHOICES = (
        ('reader', 'Reader'),
        ('editor', 'Editor'),
        ('journalist', 'Journalist'),
    )
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='reader'
        )

    subscribed_to_journalists = models.ManyToManyField(
        'eNews.Journalist', related_name='+', default=None
    )
    subscribed_to_publishers = models.ManyToManyField(
        'eNews.Publisher', related_name='+', default=None
    )

    def __str__(self):
        return self.email


class ResetToken(models.Model):
    """
    Model representing a password reset token.

    Fields:
    - token: CharField for the token with a maximum length of 255 characters.
    - expiry_date: DateTimeField for the token expiry date/time.
    - used: BooleanField set to False for whether or not the reset token has
    expired.

    Relationships:
    - user: ForeignKey representing the logged-in user.

    Methods:
    - __str__: Returns a string representation of the token, showing the
    username, token and whether or not the token has been used.

    :param models.Model: Django's base model class.
    """

    # Reference to the user who requested the password reset
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reset_tokens'
    )
    # Token string, unique to avoid duplicates
    token = models.CharField(max_length=255, unique=True)
    # When this token expires
    expiry_date = models.DateTimeField()
    # Whether this token has already been used
    used = models.BooleanField(default=False)

    def __str__(self):
        # Show a short summary for easier debugging
        return f"ResetToken(user={self.user.username}, token={self.token[:10]}..., used={self.used})"
