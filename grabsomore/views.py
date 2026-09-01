from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group, Permission  # Django's built-in user, group, and permission models
from django.contrib.auth import authenticate, login, logout  # Functions to handle login and logout
from django.http import HttpResponseRedirect  # For redirecting users or sending responses
from django.urls import reverse, reverse_lazy  # Helps get URLs by their names
from django.contrib.auth.decorators import login_required
from hashlib import sha1  # To hash tokens securely
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone  # Better way to handle dates and times in Django
from django.core.exceptions import ObjectDoesNotExist  # For handling cases when an object is not found
from .utils import generate_reset_url, build_email# Helper functions for email and token generation
from .models import ResetToken, User  # Our custom model to store reset tokens and user profiles
from django.contrib.auth.hashers import make_password  # For securely hashing passwords
from eNews.models import Journalist, Editor
from .forms import UserRegistrationForm, LoginForm


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(user=instance)


def register(request):
    """
    View to handle user registration.

    If the request method is POST, it will validate the form data and
    create a new user with the given email and password, and assign
    the user to a group based on the role given in the form data.

    If the role is 'journalist', it will create a Journalist object and
    assign it to the user. If the role is 'editor', it will create an
    Editor object and assign it to the user. If the role is 'reader', it
    will assign the user to the reader group.

    After creating the user, it will log the user in and redirect them to
    the dashboard page.

    If the request method is GET, it will render the registration form
    with an empty form.

    :param request: The HTTP request object.
    :return: An HTTP response object.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if User.objects.filter(email=form.data.get('email')).exists():
            return render(request, 'grabsomore/register.html', {'form': form, 'error': 'Email already exists'})

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['confirm_password'])  # Hash the password
            user.save()

            # Get the role from the form
            role = form.cleaned_data['role']

            # Assign permissions based on role
            if role == 'journalist':
                group, created = Group.objects.get_or_create(name='journalist')
                user.groups.add(group)

                permissions = Permission.objects.filter(codename__in=[
                    'add_articles', 'change_articles', 'view_articles', 'delete_articles',
                    'add_newsletters', 'change_newsletters', 'view_newsletters',
                    'delete_newsletters'],
                    content_type__app_label='eNews')
                group.permissions.set(permissions)

                # Create a Journalist object and assign it to the user

                journalist, created = Journalist.objects.get_or_create(journalist=user)

            elif role == 'editor':
                group, created = Group.objects.get_or_create(name='editor')
                user.groups.add(group)

                permissions = Permission.objects.filter(codename__in=[
                    'add_publishers', 'change_publishers', 'delete_publishers',
                    'view_publishers', 'delete_publishers', 'add_articles',
                    'change_articles', 'view_articles', 'delete_articles',
                    'add_newsletters', 'change_newsletters', 'view_newsletters',
                    'delete_newsletters'],
                    content_type__app_label='eNews')
                group.permissions.set(permissions)

                # Create an Editor object and assign it to the user
                editor, created = Editor.objects.get_or_create(editor=user)

            elif role == 'reader':
                group, created = Group.objects.get_or_create(name='reader')
                user.groups.add(group)

                permissions = Permission.objects.filter(codename__in=[
                    'view_articles', 'view_newsletters'],
                    content_type__app_label='eNews')
                group.permissions.set(permissions)

            login(request, user)
            return redirect('grabsomore:dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'grabsomore/register.html', {'form': form})


def user_login(request):
    """
    View to handle user login.

    If the request is a POST, then validate the form and authenticate the user.
    If the user is valid, then log them in and redirect them to the dashboard.
    If the user is invalid, then render the login page with an error message.
    If the request is a GET, then render the login page with a blank form.
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:

                login(request, user)
                return redirect('grabsomore:dashboard')
            else:
                return render(request, 'grabsomore/login.html', {'form': form, 'error': 'Invalid username or password'})
    else:
        form = LoginForm()
    return render(request, 'grabsomore/login.html', {'form': form})


def logout_user(request):
    """
    View to log user out of the application.

    :param request: HTTP request object.
    :return: Redirect to the login page of the app.
    """
    if request.user is not None:
        logout(request)  # Log out the current user
        return HttpResponseRedirect(reverse('grabsomore:login'))


@login_required(login_url=reverse_lazy('grabsomore:login'))
def dashboard(request):
    """
    View to render the dashboard for logged-in users.

    :param request: HTTP request object.
    :return: Rendered dashboard template.
    """
    is_journalist = is_journalist_view(request)
    is_editor = is_editor_view(request)
    is_reader = is_reader_view(request)

    context = {
        'is_journalist': is_journalist,
        'is_editor': is_editor,
        'is_reader': is_reader
    }

    return render(request, 'grabsomore/dashboard.html', context=context)


def send_password_reset(request):
    """
    View to to send the password reset email.

    :param request: HTTP request object.
    :return: Render the reset_email_sent confirmation page.
    """
    if request.method == 'POST':
        user_email = request.POST.get('email')
        try:
            user = User.objects.get(email=user_email)  # Find user by email
            reset_url = generate_reset_url(user)  # Generate reset link with token
            email = build_email(user, reset_url)  # Create the email message
            email.send()  # Send the email

            # Show a confirmation page that email was sent
            return render(request, 'grabsomore/reset_email_sent.html', {
                'email': user_email
            })

        except ObjectDoesNotExist:
            # Even if no user found, still show confirmation (to avoid info leaks)
            return render(request, 'grabsomore/reset_email_sent.html', {
                'email': user_email
            })

    # Show the form where user can enter their email
    return render(request, 'grabsomore/request_password_reset.html')


def reset_user_password(request, token):
    """
    View to reset the user password.

    :param request: HTTP request object.
    :param token: the password reset token.
    :return: Render the password reset form template if the password reset token
    is valid and has not expired, else render the template alligned wiith the nature of
    the reset token(invalid/expired).
    """
    hashed_token = sha1(token.encode()).hexdigest()  # Hash the token from URL

    try:
        user_token = ResetToken.objects.get(token=hashed_token)  # Look for token in DB

        # Check if the token expired
        if user_token.expiry_date < timezone.now():
            user_token.delete()  # Delete expired token
            return render(request, 'grabsomore/password_reset_expired.html')
            # Show expired token message

        # Save user ID and token in session to verify next step
        request.session['user_id'] = user_token.user.id
        request.session['reset_token'] = token

        # Show the password reset form
        return render(request, 'grabsomore/password_reset.html', {'token': token})

    except ResetToken.DoesNotExist:
        # Token not found or already used
        return render(request, 'grabsomore/password_reset_invalid.html')


def reset_password(request):
    """
    View to validate the data posted by the user in the password reset form and reset
    the password.

    :param request: HTTP request object.
    :return: Redirect to the login page if the password reset form data is valid,
    else render the login page with error message if the form data was invalid,
    else render the password_reset_expired/invalid template if the reset token is
    ivnalid or has expired.
    """
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        token = request.session.get('reset_token')
        password = request.POST.get('password')
        password_conf = request.POST.get('password_conf')

        # Check if all required data is present
        if not user_id or not token or not password or not password_conf:
            return render(request, 'grabsomore/password_reset.html', {
                'error': 'Missing fields',
            })

        # Check if passwords match
        if password != password_conf:
            return render(request, 'grabsomore/password_reset.html', {
                'error': 'Passwords do not match.',
            })

        try:
            user = User.objects.get(id=user_id)  # Find user by id
            hashed_token = sha1(token.encode()).hexdigest()
            reset_token = ResetToken.objects.get(token=hashed_token)

            # Check token expiry again (just to be sure)
            if reset_token.expiry_date < timezone.now():
                reset_token.delete()
                return render(request, 'grabsomore/password_reset_expired.html')

            # Update the user's password (hashed securely)
            user.password = make_password(password)
            user.save()

            # Delete the token and clear session info
            reset_token.delete()
            request.session.flush()

            # Redirect user to login page after successful password reset
            return HttpResponseRedirect(reverse('grabsomore:login'))

        except (User.DoesNotExist, ResetToken.DoesNotExist):
            return render(request, 'grabsomore/password_reset_invalid.html')

    # If the page was accessed with GET or any other method, redirect to login page
    return HttpResponseRedirect(reverse('grabsomore:login'))


def is_reader_view(request):
    """
    Checks if a user is a reader.

    :param request: HTTP request object.
    :return: True if the user is a reader, False otherwise.
    """
    is_reader = request.user.groups.filter(name='reader') .exists()

    return is_reader


def is_editor_view(request):
    """
    Checks if a user is an editor.

    :param request: HTTP request object.
    :return: True if the user is an editor, False otherwise.
    """
    is_editor = request.user.groups.filter(name='editor').exists()

    return is_editor


def is_journalist_view(request):
    """
    Checks if a user is a journalist.

    :param request: HTTP request object.
    :return: True if the user is a journalist, False otherwise.
    """
    is_journalist = request.user.groups.filter(name='journalist').exists()

    return is_journalist
