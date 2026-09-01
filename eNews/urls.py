from django.urls import path
from . import views

app_name = 'eNews'

urlpatterns = [
    path('view_article/<int:article_id>', views.view_article, name='article'),

    path('view_publisher/<int:publisher_id>', views.view_publisher,
         name='publisher'),

    path('view_newsletter/<int:newsletter_id>', views.view_newsletter,
         name='newsletter'),

    path('view_journalist/<int:journalist_id>', views.view_journalist,
         name='journalist'),

    path('article_list/', views.article_list, name='article_list'),

    path('publisher_list/', views.publisher_list, name='publisher_list'),

    path('journalist_list/', views.journalist_list, name='journalist_list'),

    path('newsletter_list/', views.newsletter_list, name='newsletter_list'),

    path('unapproved_article_list/', views.unapproved_article_list,
         name='unapproved_article_list'),

    path('unapproved_newsletter_list/', views.unapproved_newsletter_list,
         name='unapproved_newsletter_list'),

    path('journalist-articles/', views.journalist_articles,
         name='journalist_articles'),

    path('journalist-newsletters/', views.journalist_newsletters,
         name='journalist_newsletters'),

    path('create_article/', views.create_article, name='create_article'),

    path('create_newsletter/', views.create_newsletter,
         name='create_newsletter'),

    path('create_publisher/', views.create_publisher, name='create_publisher'),

    path('update_article/<int:article_id>', views.update_article,
         name='edit_article'),

    path('update_newsletter/<int:newsletter_id>', views.update_newsletter,
         name='edit_newsletter'),

    path('update_publisher/<int:publisher_id>', views.update_publisher,
         name='update_publisher'),

    path('delete_article/<int:article_id>', views.delete_article,
         name='delete_article'),

    path('delete_newsletter/<int:newsletter_id>', views.delete_newsletter,
         name='delete_newsletter'),

    path('delete_publisher/<int:publisher_id>', views.delete_publisher,
         name='delete_publisher'),

    path('confirm_publisher_deletion/<int:publisher_id>',
         views.confirm_publisher_deletion, name='confirm_publisher_deletion'),

    path('confirm_article_deletion/<int:article_id>',
         views.confirm_article_deletion, name='confirm_article_deletion'),

    path('confirm_newsletter_deletion/<int:newsletter_id>',
         views.confirm_newsletter_deletion,
         name='confirm_newsletter_deletion'),

    path('approve-article/<int:article_id>',
         views.article_review_approval,
         name='approve_article'),

    path('disapprove_article/<int:article_id>',
         views.article_review_disapproval, name='disapprove_article'),

    path('publish_affiliated_newsletter/<int:newsletter_id>',
         views.publish_affiliated_newsletter,
         name='publish_affiliated_newsletter'),

    path('publish_independent_article/<int:article_id>',
         views.publish_independent_article,
         name='publish_independent_article'),

    path('publish_independent_newsletter/<int:newsletter_id>',
         views.publish_independent_newsletter,
         name='publish_independent_newsletter'),

    path('subscribe_to_publisher/<int:publisher_id>',
         views.subscribe_to_publisher, name='subscribe_to_publisher'),

    path('subscribe_to_journalist/<int:journalist_id>',
         views.subscribe_to_journalist, name='subscribe_to_journalist'),

    path('unsubscribe_from_journalist/<int:journalist_id>',
         views.unsubscribe_from_journalist,
         name='unsubscribe_from_journalist'),

    path('unsubscribe_from_publisher/<int:publisher_id>',
         views.unsubscribe_from_publisher, name='unsubscribe_from_publisher'),

    path(
        'associate_journalist_with_publisher/<int:publisher_id>',
        views.associate_journalist_with_publisher,
        name='associate_journalist_with_publisher'),

    path(
        'associate_editor_with_publisher/<int:publisher_id>',
        views.associate_editor_with_publisher,
        name='associate_editor_with_publisher'),

    path(
        'dissociate_journalist_with_publisher/<int:publisher_id>',
        views.disassociate_journalist_with_publisher,
        name='dissociate_journalist_with_publisher'),

    path(
        'dissociate_editor_with_publisher/<int:publisher_id>',
        views.disassociate_editor_with_publisher,
        name='dissociate_editor_with_publisher'),

    path('api/articles/', views.api_article_list, name='api_article_list'),

    path('api/articles/subscribed/', views.subscribed_reader_articles,
         name='api_reader_articles'),

    path('api/approved/', views.api_approve_article,
         name='api_approve_article'),

    path('api/articles/<int:pk>', views.api_article_detail,
         name='api_article_detail'),

    path('api/articles/create/', views.create_api_article,
         name='api_article_create'),

    path('api/newsletters/<int:pk>', views.api_newsletter_detail,
         name='api_newsletter_detail'),

    path('api/newsletters/create/', views.create_api_newsletter,
         name='api_newsletter_create'),
]
