from django.core.mail import EmailMessage  # Used to create and send emails


def build_newsletter_email(subscriber, newsletter):
    subject = f"Newsletter: {newsletter.title}"
    body = f"{newsletter.author.first_name} {newsletter.author.last_name} Has Published A New Newsletter: {newsletter.title}"
    email = EmailMessage(subject, body, to=[subscriber.email])
    return email


def build_article_email(subscriber, article):
    subject = f"New Article: {article.title}"
    body = f"{article.author.first_name} {article.author.last_name} Has Published A New Article: {article.title}"
    email = EmailMessage(subject, body, to=[subscriber.email])
    return email
