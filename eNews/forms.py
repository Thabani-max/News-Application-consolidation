from django import forms
from .models import Article, Newsletter, Publisher


class ArticleForm(forms.ModelForm):
    """
    Form for creating or updating an article.

    Fields:
    - title: CharField for the article title.
    - content: TextField for the article content.
    Meta class:
    - Defines the model to use (Article) and the fields to include in the
    form.
    :param forms.ModelForm: Django's ModelForm class.

    """
    publisher = forms.ModelChoiceField(queryset=Publisher.objects.all(), required=False)

    class Meta:
        model = Article
        fields = ['title', 'content', 'publisher']


class NewsletterForm(forms.ModelForm):
    """
    Form for creating or updating a newsletter.

    Fields:
    - title: CharField for the newsletter title.
    - description: TextField for the newsletter description.
    Meta class:
    - Defines the model to use (Newsletter) and the fields to include in the
    form.
    :param forms.ModelForm: Django's ModelForm class.
    """
    publisher = forms.ModelChoiceField(queryset=Publisher.objects.all(), required=False)
    article = forms.ModelMultipleChoiceField(queryset=Article.objects.filter(approved=True), required=True)

    class Meta:
        model = Newsletter
        fields = ['title', 'description', 'publisher', 'article']


class PublisherForm(forms.ModelForm):
    """
    Form for creating or updating a publisher.

    Fields:
    - name: CharField for the publisher name.
    - description: TextField for the publisher description.
    Meta class:
    - Defines the model to use (Publisher) and the fields to include in the
    form.
    :param forms.ModelForm: Django's ModelForm class.
    """
    class Meta:
        model = Publisher
        fields = ['name', 'description']
