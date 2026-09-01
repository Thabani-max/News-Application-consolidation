from django.conf import settings
from django.db import models


class Article(models.Model):
    """
    Model representing a news article.

    Fields:
    - title: CharField for the article's title.
    - content: TextField for the article's content.
    - author: ForeignKey to the Author model.
    - created_at: DateTimeField for when the article was created.
    - approved: BooleanField for whether the article has been approved.
    - publisher: ForeignKey to the Publisher model.

    Methods:
    - __str__: Returns a string representation of the article, showing the
    title.

    :param models.Model: Django's base model class.
    """
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default="pending")
    publisher = models.ForeignKey(
        "Publisher", on_delete=models.CASCADE, null=True, default=None
    )

    class Meta:
        permissions = [
            ("add_articles", "Can add article"),
            ("change_articles", "Can change article"),
            ("delete_articles", "Can delete article"),
            ("view_articles", "Can view artcle"),
        ]

    def __str__(self):
        return self.title


class Publisher(models.Model):
    """
    Model representing a publisher.

    Fields:
    - name: CharField for the publisher's name.
    - description: TextField for the publisher's description.

    Methods:
    - __str__: Returns a string representation of the publisher, showing the
    name.

    :param models.Model: Django's base model class.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        permissions = [
            ("add_publishers", "Can add publisher"),
            ("change_publishers", "Can change publisher"),
            ("delete_publishers", "Can delete publisher"),
            ("view_publishers", "Can view publisher"),
        ]


class Newsletter(models.Model):
    """
    Model representing a newsletter.

    Fields:
    - title: CharField for the newsletter's title.
    - description: TextField for the newsletter's description.
    - created_at: DateTimeField for when the newsletter was created.
    - author: ForeignKey to the Author model.
    - article: ManyToManyField to the Article model.
    """
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    publisher = models.ForeignKey(
        "Publisher", on_delete=models.CASCADE, null=True, blank=True
    )
    approved = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default="pending")
    article = models.ManyToManyField("Article", blank=True)

    class Meta:
        # These are special permissions for users who can add, change, delete,
        # or view newsletters
        permissions = [
            ("add_newsletters", "Can add newsletter"),
            ("change_newsletters", "Can change newsletter"),
            ("delete_newsletters", "Can delete newsletter"),
            ("view_newsletters", "Can view newsletter"),
        ]

    def __str__(self):
        return self.title


class Journalist(models.Model):
    """
    Model representing a journalist.

    Fields:
    - publishers: ManyToManyField to the Publisher model.
    - journalist: ForeignKey to the Journalist model.

    Methods:
    - __str__: Returns a string representation of the journalist, showing the
    username.

    :param models.Model: Django's base model class.
    """
    publishers = models.ManyToManyField(Publisher, blank=True)
    journalist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.journalist.username}"


class Editor(models.Model):
    """
    Model representing an editor.

    Fields:
    - publishers: ManyToManyField to the Publisher model.
    - editor: ForeignKey to the Editor model.

    Methods:
    - __str__: Returns a string representation of the editor, showing the
    username.

    :param models.Model: Django's base model class.
    """
    publishers = models.ManyToManyField(Publisher, blank=True)
    editor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.editor.username}"
