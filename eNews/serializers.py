from rest_framework import serializers
from .models import Article, Publisher, Newsletter, Journalist, Editor


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'


class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = '__all__'


class JournalistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journalist
        fields = '__all__'


class EditorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Editor
        fields = '__all__'