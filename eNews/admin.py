from django.contrib import admin
from .models import Article, Newsletter, Publisher, Journalist, Editor

# Register your models here.
admin.site.register(Article)
admin.site.register(Newsletter)
admin.site.register(Publisher)
admin.site.register(Journalist)
admin.site.register(Editor)
