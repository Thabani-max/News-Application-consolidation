from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db.models import Q
from .utils import build_article_email, build_newsletter_email
from .models import Article, Publisher, Newsletter, Journalist, Editor
from grabsomore.models import User
from .forms import ArticleForm, NewsletterForm, PublisherForm
import requests
# api imorts
from rest_framework.response import Response
from .serializers import ArticleSerializer, NewsletterSerializer
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.authtoken.models import Token


def create_article(request):
    """
    View to create a new article.

    The user is assumed to be a journalist. The article is saved with the
    current user as the journalist.

    :param request: HTTP request object.
    :return: Redirect to the dashboard after saving.
    """
    is_journalist = is_journalist_view(request)
    is_editor = is_editor_view(request)
    is_reader = is_reader_view(request)

    if request.method == 'POST':
        form = ArticleForm(request.POST)

        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()

            return redirect('grabsomore:dashboard')
    else:
        form = ArticleForm()

    context = {
        'is_editor': is_editor,
        'is_reader': is_reader,
        'is_journalist': is_journalist,
        'form': form
    }

    return render(request, 'eNews/create_article.html', context=context)


def create_newsletter(request):
    """
    View to create a new newsletter.
    The user is assumed to be a journalist or an editor.

    :param request: HTTP request object.
    :return: Redirect to the dashboard after saving.
    """
    is_journalist = is_journalist_view(request)
    is_editor = is_editor_view(request)
    is_reader = is_reader_view(request)
    articles = Article.objects.all()
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.author = request.user
            newsletter.save()

            # get the article in the form and add it's id to the newsletter
            for article_id in request.POST.getlist('article'):
                article = get_object_or_404(Article, pk=article_id)
                newsletter.article.add(article)

            return redirect('grabsomore:dashboard')
    else:
        form = NewsletterForm()
        context = {
            'is_editor': is_editor,
            'is_reader': is_reader,
            'is_journalist': is_journalist,
            'form': form,
            'articles': articles
        }
    return render(request, 'eNews/create_newsletter.html', context=context)


def create_publisher(request):
    """
    View to create a new publisher.

    :param request: HTTP request object.
    :return: Redirect to the dashboard after saving.
    """
    is_editor = is_editor_view(request)
    is_reader = is_reader_view(request)
    is_journalist = is_journalist_view(request)
    if request.method == 'POST':
        form = PublisherForm(request.POST)
        if form.is_valid():
            form.save()
            # add the newly created publisher to the editor's publisher field
            publsher_name = form.cleaned_data['name']
            editor = get_object_or_404(Editor, editor=request.user)
            publisher = get_object_or_404(Publisher, name=publsher_name)
            editor.publishers.add(publisher)
            return redirect('grabsomore:dashboard')
    else:
        form = PublisherForm()
        context = {
            'is_editor': is_editor,
            'is_reader': is_reader,
            'is_journalist': is_journalist,
            'form': form
        }

    return render(request, 'eNews/create_publisher.html', context=context)


def publisher_list(request):
    """
    View to render a list of all publishers in the database.

    :param request: HTTP request object.
    :return: Rendered template with a list of all publishers.
    """
    is_editor = is_editor_view(request)
    is_reader = is_reader_view(request)
    is_journalist = is_journalist_view(request)
    publishers = Publisher.objects.all()
    context = {
        'publishers': publishers,
        'is_editor': is_editor,
        'is_reader': is_reader,
        'is_journalist': is_journalist
    }
    return render(request, 'eNews/publisher_list.html', context=context)


def journalist_list(request):
    """
    View to render a list of all journalists in the database.

    :param request: HTTP request object.
    :return: Rendered template with a list of all journalists.
    """
    is_editor = is_editor_view(request)
    is_reader = is_reader_view(request)
    is_journalist = is_journalist_view(request)
    journalists = Journalist.objects.all()
    context = {
        'journalists': journalists,
        'is_editor': is_editor,
        'is_reader': is_reader,
        'is_journalist': is_journalist
    }
    return render(request, 'eNews/journalist_list.html', context=context)


def article_list(request):
    """
    View to render a list of all articles in the database.

    :param request: HTTP request object.
    :return: Rendered template with a list of all articles.
    """
    is_editor = is_editor_view(request)
    is_reader = is_reader_view(request)
    is_journalist = is_journalist_view(request)
    articles = Article.objects.filter(approved=True).all()
    context = {
        'articles': articles,
        'is_editor': is_editor,
        'is_reader': is_reader,
        'is_journalist': is_journalist
    }
    return render(request, 'eNews/article_list.html', context=context)


def newsletter_list(request):
    """
    View to render a list of all newsletters in the database.

    :param request: HTTP request object.
    :return: Rendered template with a list of all newsletters.
    """
    is_editor = is_editor_view(request)
    is_reader = is_reader_view(request)
    is_journalist = is_journalist_view(request)
    newsletters = Newsletter.objects.filter(approved=True).all()
    context = {
        'newsletters': newsletters,
        'is_editor': is_editor,
        'is_reader': is_reader,
        'is_journalist': is_journalist
    }
    return render(request, 'eNews/newsletter_list.html', context=context)


def newsletter_articles_list(newsletter_id):
    """
    View to render a list of all articles in a specific newsletter in the
    database.

    :param request: HTTP request object.
    :param newsletter_id: The ID of the newsletter to be rendered.
    :return: Rendered template with a list of all articles in the specified
    newsletter.
    """
    # get all articles of a specific newsletter from the database
    newsletter = Newsletter.objects.get(pk=newsletter_id)
    article = newsletter.article.filter(approved=True).all()

    return article


# The function that retrieves all articles that belong to a specific publisher
def publisher_articles_list(publisher_id):
    """
    View to render a list of all articles in a specific publisher in the
    database.

    :param request: HTTP request object.
    :param publisher_id: The ID of the publisher to be rendered.
    :return: Rendered template with a list of all articles in the specified
    publisher.
    """
    article = Article.objects.filter(publisher=publisher_id, approved=True).all()

    return article


# The function that retrieves all articles that belong to a specific journalist
def journalist_articles_list(journalist_id):
    """
    View to render a list of all articles in a specific journalist in the
    database.

    :param request: HTTP request object.
    :param journalist_id: The ID of the journalist to be rendered.
    :return: Rendered template with a list of all articles in the specified
    ournalist.
    """
    journalist = Journalist.objects.get(pk=journalist_id)
    article = Article.objects.filter(author=journalist.journalist, approved=True).all()

    return article


def journalist_newsletters(request):
    """
    View to render a list of all newsletters in a specific journalist in the database.

    :param request: HTTP request object.
    :param journalist_id: The ID of the journalist to be rendered.
    :return: Rendered template with a list of all newsletters in the specified journalist.
    """
    user = request.user
    journalist = get_object_or_404(Journalist, journalist=user.id)

    newsletters = Newsletter.objects.filter(author=journalist.journalist)

    context = {
        'newsletters': newsletters
    }

    return render(request, 'eNews/journalist_newsletters.html', context=context)


def journalist_articles(request):
    """
    View to render a list of all articles in a specific journalist in the database.

    :param request: HTTP request object.
    :param journalist_id: The ID of the journalist to be rendered.
    :return: Rendered template with a list of all articles in the specified journalist.
    """
    user = request.user
    journalist = get_object_or_404(Journalist, journalist=user.id)

    articles = Article.objects.filter(author=journalist.journalist)

    context = {
        'articles': articles
    }

    return render(request, 'eNews/journalist_articles.html', context=context)


def publisher_newsletter_list(publisher_id):
    """
    View to render a list of all newsletters in a specific publisher in the
    database.

    :param request: HTTP request object.
    :param publisher_id: The ID of the publisher to be rendered.
    :return: Rendered template with a list of all newsletters in the specified
    publisher.
    """
    newsletter = Newsletter.objects.filter(publisher=publisher_id, approved=True).all()

    return newsletter


def journalist_newsletter_list(journalist_id):
    """
    View to render a list of all newsletters in a specific journalist in the database.

    :param request: HTTP request object.
    :param journalist_id: The ID of the journalist to be rendered.
    :return: Rendered template with a list of all newsletters in the specified journalist.
    """
    journalist = Journalist.objects.get(pk=journalist_id)
    newsletter = Newsletter.objects.filter(author=journalist.journalist, approved=True).all()

    return newsletter


def publisher_journalist_list(publisher_id):
    """
    View to render a list of all journalists in a specific publisher in the database.

    :param request: HTTP request object.
    :param publisher_id: The ID of the publisher to be rendered.
    :return: Rendered template with a list of all journalists in the specified publisher.
    """
    journalist = Journalist.objects.filter(publishers=publisher_id).all()

    return journalist


def view_publisher(request, publisher_id):
    """
    View to render a specific publisher in the database.

    :param request: HTTP request object.
    :param publisher_id: The ID of the publisher to be rendered.
    :return: Rendered template with the specified publisher.
    """
    is_editor = is_editor_view(request)
    is_reader = is_reader_view(request)
    is_journalist = is_journalist_view(request)
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    articles = publisher_articles_list(publisher_id)
    newsletters = publisher_newsletter_list(publisher_id)
    journalists = publisher_journalist_list(publisher_id)

    if is_reader:
        is_subscribed = is_subscribed_to_publisher(request, publisher_id)
        context = {
            'publisher': publisher,
            'is_editor': is_editor,
            'is_reader': is_reader,
            'is_journalist': is_journalist,
            'is_subscribed': is_subscribed,
            'articles': articles,
            'newsletters': newsletters,
            'journalists': journalists
        }

        return render(request, 'eNews/view_publisher.html', context=context)

    elif is_journalist:
        is_associated_with_publisher = is_journalist_associated_with_publisher(publisher_id)

        context = {
            'publisher': publisher,
            'is_editor': is_editor,
            'is_reader': is_reader,
            'is_journalist': is_journalist,
            'is_associated_with_publisher': is_associated_with_publisher,
            'articles': articles,
            'newsletters': newsletters,
            'journalists': journalists
        }

        return render(request, 'eNews/view_publisher.html', context=context)

    else:
        is_associated_with_publisher = is_editor_associated_with_publisher(publisher_id)
        context = {
            'publisher': publisher,
            'is_editor': is_editor,
            'is_reader': is_reader,
            'is_journalist': is_journalist,
            'is_associated_with_publisher': is_associated_with_publisher,
            'articles': articles,
            'newsletters': newsletters,
            'journalists': journalists
        }

        return render(request, 'eNews/view_publisher.html', context=context)


def view_journalist(request, journalist_id):
    """
    View to render a specific journalist in the database.

    :param request: HTTP request object.
    :param journalist_id: The ID of the journalist to be rendered.
    :return: Rendered template with the specified journalist.
    """
    is_editor = is_editor_view(request)
    is_reader = is_reader_view(request)
    is_journalist = is_journalist_view(request)
    journalist = get_object_or_404(Journalist, pk=journalist_id)
    is_subscribed = is_subscribed_to_journalist(request, journalist_id)
    articles = journalist_articles_list(journalist_id)
    newsletter = journalist_newsletter_list(journalist_id)

    if is_reader:
        is_subscribed = is_subscribed_to_journalist(request, journalist_id)
        context = {
            'journalist': journalist,
            'is_editor': is_editor,
            'is_reader': is_reader,
            'is_journalist': is_journalist,
            'is_subscribed': is_subscribed,
            'articles': articles,
            'newsletters': newsletter,
        }

        return render(request, 'eNews/view_journalist.html', context=context)

    else:
        context = {
            'journalist': journalist,
            'is_editor': is_editor,
            'is_reader': is_reader,
            'is_journalist': is_journalist,
            'articles': articles,
            'newsletters': newsletter,
        }

        return render(request, 'eNews/view_journalist.html', context=context)


def view_article(request, article_id):
    """
    View to render a specific article in the database.

    :param request: HTTP request object.
    :param article_id: The ID of the article to be rendered.
    :return: Rendered template with the specified article.
    """
    article = get_object_or_404(Article, pk=article_id)
    is_editor = is_editor_view(request)
    is_reader = is_reader_view(request)
    is_journalist = is_journalist_view(request)

    context = {
        'article': article,
        'is_editor': is_editor,
        'is_reader': is_reader,
        'is_journalist': is_journalist,
    }

    return render(request, 'eNews/view_article.html', context=context)


def view_newsletter(request, newsletter_id):
    """
    View to render a specific newsletter in the database.

    :param request: HTTP request object.
    :param newsletter_id: The ID of the newsletter to be rendered.
    :return: Rendered template with the specified newsletter.
    """
    newsletter = get_object_or_404(Newsletter, pk=newsletter_id)
    is_editor = is_editor_view(request)
    is_reader = is_reader_view(request)
    is_journalist = is_journalist_view(request)
    articles = newsletter_articles_list(newsletter_id)

    context = {
        'newsletter': newsletter,
        'is_editor': is_editor,
        'is_reader': is_reader,
        'is_journalist': is_journalist,
        'articles': articles,
    }

    return render(request, 'eNews/view_newsletter.html', context=context)


def update_article(request, article_id):
    """
    View to update an article in the database.

    :param request: HTTP request object.
    :param article_id: The ID of the article to be updated.
    :return: Redirect to the list of articles after saving.
    """
    is_editor = is_editor_view(request)
    is_reader = is_reader_view(request)
    is_journalist = is_journalist_view(request)
    article = get_object_or_404(Article, pk=article_id)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        context = {
            'is_editor': is_editor,
            'is_reader': is_reader,
            'is_journalist': is_journalist,
            'form': form,
            'article': article
        }
        if form.is_valid():
            form.save()
            return redirect('eNews:article_list')
    else:
        form = ArticleForm(instance=article)
        context = {
            'is_editor': is_editor,
            'is_reader': is_reader,
            'is_journalist': is_journalist,
            'form': form,
            'article': article
        }
    return render(request, 'eNews/update_article.html', context=context)


def update_newsletter(request, newsletter_id):
    """
    View to update a newsletter in the database.

    :param request: HTTP request object.
    :param newsletter_id: The ID of the newsletter to be updated.
    :return: Redirect to the list of newsletters after saving.
    """
    is_editor = is_editor_view(request)
    is_reader = is_reader_view(request)
    is_journalist = is_journalist_view(request)
    newsletter = get_object_or_404(Newsletter, pk=newsletter_id)
    if request.method == 'POST':
        form = NewsletterForm(request.POST, instance=newsletter)
        context = {
            'is_editor': is_editor,
            'is_reader': is_reader,
            'is_journalist': is_journalist,
            'form': form,
            'newsletter': newsletter
        }
        if form.is_valid():
            form.save()
            return redirect('eNews:newsletter_list')
    else:
        form = NewsletterForm(instance=newsletter)
        context = {
            'is_editor': is_editor,
            'is_reader': is_reader,
            'is_journalist': is_journalist,
            'form': form,
            'newsletter': newsletter
        }
    return render(request, 'eNews/update_newsletter.html', context=context)


def update_publisher(request, publisher_id):
    """
    View to update a publisher in the database.

    :param request: HTTP request object.
    :param publisher_id: The ID of the publisher to be updated.
    :return: Redirect to the list of publishers after saving.
    """
    is_editor = is_editor_view(request)
    is_reader = is_reader_view(request)
    is_journalist = is_journalist_view(request)
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    if request.method == 'POST':
        form = PublisherForm(request.POST, instance=publisher)
        context = {
            'is_editor': is_editor,
            'is_reader': is_reader,
            'is_journalist': is_journalist,
            'form': form,
            'publisher': publisher
        }
        if form.is_valid():
            form.save()
            return redirect('eNews:publisher_list')
    else:
        form = PublisherForm(instance=publisher)
        context = {
            'is_editor': is_editor,
            'is_reader': is_reader,
            'is_journalist': is_journalist,
            'form': form,
            'publisher': publisher
        }
    return render(request, 'eNews/update_publisher.html', context=context)


def delete_article(request, article_id):
    """
    View to delete an article by first checking if the user is a journalist or
    an editor then asking the user to confirm the deletion.

    :param request: HTTP request object.
    :param article_id: The ID of the article to be deleted.
    :return: Redirect to the confirmation page for article deletion.
    """
    article = get_object_or_404(Article, pk=article_id)

    return render(request, 'eNews/confirm_delete_article.html',
                  {'article': article})


def confirm_article_deletion(request, article_id):
    """
    View to confirm the deletion of an article.

    :param request: HTTP request object.
    :param article_id: The ID of the article to be deleted.
    :return: Redirect to the article list page after deletion.
    """
    article = get_object_or_404(Article, pk=article_id)

    if request.method == 'POST':
        article.delete()
        return HttpResponseRedirect(reverse('eNews:article_list'))

    return render(request, 'eNews/confirm_delete_article.html',
                  {'article': article})


def delete_newsletter(request, newsletter_id):
    """
    View to delete a newsletter by first checking if the user is a journalist
    or an editor then asking the user to confirm the deletion.

    :param request: HTTP request object.
    :param newsletter_id: The ID of the newsletter to be deleted.
    :return: Redirect to the confirmation page for newsletter deletion.
    """
    newsletter = get_object_or_404(Newsletter, pk=newsletter_id)

    return render(request, 'eNews/confirm_delete_newsletter.html',
                  {'newsletter': newsletter})


def confirm_newsletter_deletion(request, newsletter_id):
    """
    View to confirm the deletion of a newsletter.

    :param request: HTTP request object.
    :param newsletter_id: The ID of the newsletter to be deleted.
    :return: Redirect to the newsletter list page after deletion.
    """
    newsletter = get_object_or_404(Newsletter, pk=newsletter_id)

    if request.method == 'POST':
        newsletter.delete()
        return HttpResponseRedirect(reverse('eNews:newsletter_list'))

    return render(request, 'eNews/confirm_delete_newsletter.html',
                  {'newsletter': newsletter})


def delete_publisher(request, publisher_id):
    """
    View to delete a publisher by first checking if the user is
    an editor then asking the user to confirm the deletion.

    :param request: HTTP request object.
    :param publisher_id: The ID of the publisher to be deleted.
    :return: Redirect to the confirmation page for publisher deletion.
    """
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    return render(request, 'eNews/confirm_delete_publisher.html',
                  {'publisher': publisher})


def confirm_publisher_deletion(request, publisher_id):
    """
    View to confirm the deletion of a publisher.

    :param request: HTTP request object.
    :param publisher_id: The ID of the publisher to be deleted.
    :return: Redirect to the publisher list page after deletion.
    """
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    if request.method == 'POST':
        publisher.delete()
        return HttpResponseRedirect(reverse('eNews:publisher_list'))

    return render(request, 'eNews/confirm_delete_publisher.html',
                  {'publisher': publisher})


def unapproved_article_list(request):
    """
    View to render a list of all articles in the database.

    :param request: HTTP request object.
    :return: Rendered template with a list of all articles.
    """
    articles = Article.objects.filter(approved=False)
    return render(request, 'eNews/unapproved_article_list.html',
                  {'articles': articles})


def unapproved_newsletter_list(request):
    """
    View to render a list of all newsletters in the database.

    :param request: HTTP request object.
    :return: Rendered template with a list of all newsletters.
    """
    newsletters = Newsletter.objects.filter(approved=False)
    return render(request, 'eNews/unapproved_newsletter_list.html',
                  {'newsletters': newsletters})


def get_journalist_subscribers(request, journalist_id):
    """
    Function to get a list of all subscribers to a specific journalist.

    :param request: HTTP request object.
    :param journalist_id: The ID of the journalist to get the subscribers of.
    :return: A list of all subscribers to the specified journalist.
    """

    subscribers_list = []
    subscribers = User.objects.filter(subscribed_to_journalists=journalist_id)
    # Append the subscribers to the subscribers_list
    for subscriber in subscribers:
        subscribers_list.append(subscriber)

    return subscribers_list


def get_publisher_subscribers(request, publisher_id):
    """
    Function to get a list of all subscribers to a specific publisher.

    :param request: HTTP request object.
    :param publisher_id: The ID of the publisher to get the subscribers of.
    :return: A list of all subscribers to the specified publisher.
    """

    subscribers_list = []

    # Get all users with the publisher id in their subscribed_publishers field
    subscribers = User.objects.filter(subscribed_to_publishers=publisher_id)
    # Append the subscribers to the subscribers_list
    for subscriber in subscribers:
        subscribers_list.append(subscriber)
    return subscribers_list


def article_review_approval(request, article_id):
    """
    View to approve an article by first checking if the user
    an editor then approving the areticle and emails it to the
    subscribers of the article journalist and/ or publisher
    and then sends a post request to the api

    :param request: HTTP request object.
    :param article_id: The ID of the article to be approved.
    :return: Redirect to the list of unapproved articles.
    """
    article = get_object_or_404(Article, pk=article_id)
    if request.method == 'POST':
        article.approved = True
        article.status = "Approved"
        article.save()

        # Send a POST request to the api
        token, created = Token.objects.get_or_create(user=request.user)
        url = 'http://127.0.0.1:8000/api/approved/'
        headers = {'Authorization': f'Token {token}'}

        author_id = article.author.id
        publisher_id = article.publisher.id

        data = {
            'id': article.id,
            'title': article.title,
            'author': author_id,
            'content': article.content,
            'publisher': publisher_id,
            'approved': True,
            'status': "Approved"
        }

        response = requests.post(url, json=data, headers=headers)

        print("Approved article")
        print(response.json())

        journalist_id = Journalist.objects.get(journalist=article.author).id
        journalist_subscribers = get_journalist_subscribers(request,
                                                            journalist_id)
        if article.publisher:
            publisher_subscribers = get_publisher_subscribers(request,
                                                              article.publisher)
            print(publisher_subscribers)
            if len(publisher_subscribers) > 0:
                for subscriber in publisher_subscribers:
                    build_article_email(subscriber, article).send()

        print(journalist_subscribers)
        if len(journalist_subscribers) > 0:
            for subscriber in journalist_subscribers:
                build_article_email(subscriber, article).send()

        article.delete()

        return HttpResponseRedirect(reverse('eNews:unapproved_article_list'))
    return render(request, 'eNews/view_article.html',
                  context={'error': 'Failed to approve article',
                           'article': article})


def article_review_disapproval(request, article_id):
    """
    View to disapprove an article by first checking if the user is
    an editor.

    :param request: HTTP request object.
    :param article_id: The ID of the article to be disapproved.
    :return: Redirect to the list of unapproved articles.
    """
    article = get_object_or_404(Article, pk=article_id)
    if request.method == 'POST':
        article.approved = False
        article.status = "Disapproved"
        article.save()
        return HttpResponseRedirect(reverse('eNews:unapproved_article_list'))
    return render(request, 'eNews/view_article.html', {'article': article})


def publish_affiliated_newsletter(request, newsletter_id):
    """
    A view for journalists to publish a newsletter under a publisher.
    The published newsletter is then sent to the subscribers of the
    journalist and/ or publisher

    :param request: HTTP request object.
    :param newsletter_id: The ID of the newsletter to be published.
    :return: Redirect to the list of newsletters.

    """

    newsletter = get_object_or_404(Newsletter, pk=newsletter_id)
    if request.method == 'POST':
        newsletter.approved = True
        newsletter.save()
        newsletter.status = "Approved"
        newsletter.save()

        journalist_id = Journalist.objects.get(journalist=newsletter.author).id
        journalist_subscribers = get_journalist_subscribers(request,
                                                            journalist_id)
        if newsletter.publisher:
            publisher_subscribers = get_publisher_subscribers(request,
                                                              newsletter.publisher)
            print(publisher_subscribers)
            if len(publisher_subscribers) > 0:
                for subscriber in publisher_subscribers:
                    build_newsletter_email(subscriber, newsletter).send()

        print(journalist_subscribers)
        if len(journalist_subscribers) > 0:
            for subscriber in journalist_subscribers:
                build_newsletter_email(subscriber, newsletter).send()

        return HttpResponseRedirect(reverse('eNews:newsletter_list'))
    return render(request, 'eNews/view_newsletter.html',
                  {'newsletter': newsletter})


def publish_independent_article(request, article_id):
    """
    A view for journalists to publish an article independently.
    The published article is then sent to the subscribers of the
    journalist and/ or publisher

    :param request: HTTP request object.
    :param article_id: The ID of the article to be published.
    :return: Redirect to the list of articles.
    """
    article = get_object_or_404(Article, pk=article_id)
    if request.method == 'POST':

        article.approved = True
        article.save()
        article.status = "Approved"
        article.save()
        article.publisher = None
        article.save()

        journalist_id = Journalist.objects.get(journalist=article.author).id

        journalist_subscribers = get_journalist_subscribers(request,
                                                            journalist_id)
        for subscriber in journalist_subscribers:
            build_article_email(subscriber, article).send()
        return HttpResponseRedirect(reverse('eNews:journalist_articles'))
    return render(request, 'eNews/view_article.html', {'article': article})


def publish_independent_newsletter(request, newsletter_id):
    """
    A view to publish a newsletter independently. The published
    newsletter is then emailed to the subscribers of the journalist

    :param request: HTTP request object.
    :param newsletter_id: The ID of the newsletter to be published.
    :return: Redirect to the list of newsletters.
    """

    newsletter = get_object_or_404(Newsletter, pk=newsletter_id)
    if request.method == 'POST':

        newsletter.approved = True
        newsletter.save()
        newsletter.status = "Approved"
        newsletter.save()
        newsletter.publisher = None
        newsletter.save()

        journalist_id = Journalist.objects.get(journalist=newsletter.author).id

        journalist_subscribers = get_journalist_subscribers(request, journalist_id)
        for subscriber in journalist_subscribers:
            build_newsletter_email(subscriber, newsletter).send()
        return HttpResponseRedirect(reverse('eNews:journalist_newsletters'))
    return render(request, 'eNews/view_newsletter.html', {'newsletter': newsletter})


def subscribe_to_journalist(request, journalist_id):
    """
    View to subscribe to a journalist.

    :param request: HTTP request object.
    :param journalist_id: The ID of the journalist to be subscribed to.
    :return: Redirect to the journalist list page after subscription.
    """
    journalist = get_object_or_404(Journalist, pk=journalist_id)
    request.user.subscribed_to_journalists.add(journalist)
    return HttpResponseRedirect(reverse('eNews:journalist_list'))


def unsubscribe_from_journalist(request, journalist_id):
    """
    View to unsubscribe from a journalist.

    :param request: HTTP request object.
    :param journalist_id: The ID of the journalist to be unsubscribed from.
    :return: Redirect to the journalist list page after unsubscription.
    """
    journalist = get_object_or_404(Journalist, pk=journalist_id)
    request.user.subscribed_to_journalists.remove(journalist)
    return HttpResponseRedirect(reverse('eNews:journalist_list'))


def subscribe_to_publisher(request, publisher_id):
    """
    View to subscribe to a publisher.

    :param request: HTTP request object.
    :param publisher_id: The ID of the publisher to be subscribed to.
    :return: Redirect to the publisher list page after subscription.
    """
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    request.user.subscribed_to_publishers.add(publisher)
    return HttpResponseRedirect(reverse('eNews:publisher_list'))


def unsubscribe_from_publisher(request, publisher_id):
    """
    View to unsubscribe from a publisher.

    :param request: HTTP request object.
    :param publisher_id: The ID of the publisher to be unsubscribed from.
    :return: Redirect to the publisher list page after unsubscription.
    """
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    request.user.subscribed_to_publishers.remove(publisher)
    return HttpResponseRedirect(reverse('eNews:publisher_list'))


def is_subscribed_to_journalist(request, journalist_id):
    """
    Checks if a user is subscribed to a specific journalist.

    :param request: HTTP request object.
    :param journalist_id: The ID of the journalist to check subscription for.
    :return: True if the user is subscribed to the journalist, False otherwise.
    """
    is_subscribed_to_journalist = request.user.subscribed_to_journalists.filter(pk=journalist_id).exists()

    return is_subscribed_to_journalist


def is_subscribed_to_publisher(request, publisher_id):
    """
    Checks if a user is subscribed to a specific publisher.

    :param request: HTTP request object.
    :param publisher_id: The ID of the publisher to check subscription for.
    :return: True if the user is subscribed to the publisher, False otherwise.
    """
    is_subscribed_to_publisher = request.user.subscribed_to_publishers.filter(pk=publisher_id).exists()

    return is_subscribed_to_publisher


def is_reader_view(request):
    """
    Checks if a user is a reader.

    :param request: HTTP request object.
    :return: True if the user is a reader, False otherwise.
    """
    is_reader = request.user.groups.filter(name='reader').exists()

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


def associate_journalist_with_publisher(request, publisher_id):
    """
    A view for journalists to affiliate with a publisher.

    :param request: HTTP request object.
    :param publisher_id: The ID of the publisher to be associated with.
    :return: Redirect to the publisher list page.
    """
    journalist = get_object_or_404(Journalist, journalist=request.user.id)
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    journalist.publishers.add(publisher)

    return HttpResponseRedirect(reverse('eNews:publisher_list'))


def associate_editor_with_publisher(request, publisher_id):
    """
    A view to associate an editor with a publisher.

    :param request: HTTP request object.
    :param publisher_id: The ID of the publisher to be associated with.
    :return: Redirect to the publisher list page.
    """
    # add the publisher to the editor's publisher field
    editor = get_object_or_404(Editor, editor=request.user.id)
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    editor.publishers.add(publisher)

    return HttpResponseRedirect(reverse('eNews:publisher_list'))


def disassociate_journalist_with_publisher(request, publisher_id):
    """
    A view for journalists to dissociate from a publisher.

    :param request: HTTP request object.
    :param publisher_id: The ID of the publisher to be dissociated from.
    :return: Redirect to the publisher list page.
    """
    journalist = get_object_or_404(Journalist, journalist=request.user.id)
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    journalist.publishers.remove(publisher)

    return HttpResponseRedirect(reverse('eNews:publisher_list'))


def disassociate_editor_with_publisher(request, publisher_id):
    """
    A view for editors to dissociate from a publisher.

    :param request: HTTP request object.
    :param publisher_id: The ID of the publisher to be dissociated from.
    :return: Redirect to the publisher list page.
    """
    editor = get_object_or_404(Editor, editor=request.user.id)
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    editor.publishers.remove(publisher)

    return HttpResponseRedirect(reverse('eNews:publisher_list'))


def is_journalist_associated_with_publisher(publisher_id):
    """
    Checks if a journalist is associated with a specific publisher.

    :param publisher_id: The ID of the publisher to check association for.
    :return: True if the journalist is associated with the publisher, False otherwise.
    """
    is_associated_with_publisher = Journalist.objects.filter(publishers=publisher_id).exists()

    return is_associated_with_publisher


def is_editor_associated_with_publisher(publisher_id):
    """
    Checks if an editor is associated with a specific publisher.

    :param publisher_id: The ID of the publisher to check association for.
    :return: True if the editor is associated with the publisher, False otherwise.
    """
    is_associated_with_editor = Editor.objects.filter(publishers=publisher_id).exists()

    return is_associated_with_editor


# Get article list API Views
@api_view(['GET'])
def api_article_list(request):
    """
    API View to get the list of approved articles.

    :param request: HTTP request object.
    :return: JSON response containing the list of approved articles.
    :rtype: Response
    """
    articles = Article.objects.filter(approved=True)
    serializer = ArticleSerializer(articles, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)
    # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Get subscribed reader articles
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def subscribed_reader_articles(request):
    """
    API View to get the list of approved articles that the user is subscribed
    to.

    The user must be authenticated and have the role 'reader' to access this
    view.

    :param request: HTTP request object.
    :return: JSON response containing the list of approved articles that the
    user is subscribed to.
    :rtype: Response
    :raises: HTTP_403_FORBIDDEN if the user is not a reader.
    """
    journalists = request.user.subscribed_to_journalists.all()
    publishers = request.user.subscribed_to_publishers.all()
    articles = Article.objects.filter(approved=True).filter(
        Q(author__journalist__in=journalists) | Q(publisher__in=publishers)
    ).distinct()

    if request.user.role == 'reader':

        serializer = ArticleSerializer(articles, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'You are not a reader'},
                        status=status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_article_detail(request, pk):
    """
    API View to get, update, or delete an article.

    :param request: HTTP request object.
    :param pk: The ID of the article to be retrieved, updated, or deleted.
    :return: JSON response containing the article data if the request method
    is GET,
    JSON response containing the updated article data if the request method is
    PUT, or an empty response if the request method is DELETE.
    :rtype: Response
    :raises: HTTP_403_FORBIDDEN if the user is not an editor or journalist.
    """
    article = get_object_or_404(Article, pk=pk)

    if request.method == 'GET':
        serializer = ArticleSerializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'PUT':
        if request.user.role != 'editor' and request.user.role != 'journalist':
            return Response({'error': 'You are not a journalist or editor'},
                            status=status.HTTP_403_FORBIDDEN)
        else:
            serializer = ArticleSerializer(article, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        if request.user.role != 'editor' and request.user.role != 'journalist':
            return Response({'error': 'You are not a journalist or editor'},
                            status=status.HTTP_403_FORBIDDEN)
        else:
            article.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_api_article(request):
    """
    API View to create a new article.

    :param request: HTTP request object.
    :return: JSON response containing the created article data if the request
    is valid, or JSON response containing the errors if the request is invalid.
    :rtype: Response
    :raises: HTTP_403_FORBIDDEN if the user is not a journalist.
    """
    if request.user.role != 'journalist':
        return Response({'error': 'You are not a journalist'},
                        status=status.HTTP_403_FORBIDDEN)

    serializer = ArticleSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_approve_article(request):
    """
    API View to approve an article.

    The user must be an editor to access this view.

    :param request: HTTP request object.
    :return: JSON response containing the approved article data if the request
    is valid, or JSON response containing the errors if the request is invalid.
    :rtype: Response
    :raises: HTTP_403_FORBIDDEN if the user is not an editor.
    """
    if request.user.role != 'editor':
        return Response({'error': 'You are not an editor'},
                        status=status.HTTP_403_FORBIDDEN)

    serializer = ArticleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_api_newsletter(request):
    """
    API View to create a new newsletter.

    The user must be a journalist to access this view.

    :param request: HTTP request object.
    :return: JSON response containing the created newsletter data if the
    request is valid, or JSON response containing the errors if the request is invalid.
    :rtype: Response
    :raises: HTTP_403_FORBIDDEN if the user is not a journalist.
    """
    if request.user.role != 'journalist':
        return Response({'error': 'You are not a journalist'},
                        status=status.HTTP_403_FORBIDDEN)
    serializer = NewsletterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_newsletter_detail(request, pk):

    """
    API View to get, update, or delete a newsletter.

    :param request: HTTP request object.
    :param pk: The ID of the newsletter to be retrieved, updated, or deleted.
    :return: JSON response containing the newsletter data if the request method
    is GET,
    JSON response containing the updated newsletter data if the request method
    is PUT, or an empty response if the request method is DELETE.
    :rtype: Response
    :raises: HTTP_403_FORBIDDEN if the user is not a journalist or editor.
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)

    if request.method == 'GET':
        serializer = NewsletterSerializer(newsletter)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'PUT':
        if request.user.role != 'editor' and request.user.role != 'journalist':
            return Response({'error': 'You are not a journalist or editor'},
                            status=status.HTTP_403_FORBIDDEN)
        else:
            serializer = NewsletterSerializer(newsletter, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        if request.user.role != 'editor' and request.user.role != 'journalist':
            return Response({'error': 'You are not a journalist or editor'},
                            status=status.HTTP_403_FORBIDDEN)
        else:
            newsletter.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
