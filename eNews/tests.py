from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from grabsomore.models import User
from .models import Article, Newsletter, Journalist, Publisher
from rest_framework.authtoken.models import Token


class ArticleTests(APITestCase):
    def setUp(self):
        """
        Create reader, journalist, and editor users, as well as approved
        and unapproved articles for testing. This sets up the conditins to test
        the API views
        """

        # create reader user
        self.user = User.objects.create_user(
            username='testuser', role='reader', password='testpassword',
            email='testemail@.com', first_name='testfirst',
            last_name='testlast')

        # create journalist user
        self.user_two = User.objects.create_user(
            username='testuser2', role='journalist', password='testpassword',
            email='testemail02@.com', first_name='testfirst2',
            last_name='testlast2')

        # create journalist object from user
        self.journalist, created = Journalist.objects.get_or_create(journalist=self.user_two)
        self.journalist.save()

        # create publisher user
        self.publisher, created = Publisher.objects.get_or_create(name='Test Publisher',
                                                                   description='This is a test publisher.')
        self.publisher.save()
        # create editor user
        self.user_three = User.objects.create_user(
            username='testuser3', role='editor', password='testpassword',
            email='testemail03@.com', first_name='testfirst3',
            last_name='testlast3')

        # create unapproved article
        self.article = Article.objects.create(
            title='Test Article', content='This is a test article.',
            author=self.user_two,
            approved=True, status='Approved')
        self.article.save()

        # create approved article
        self.article_two = Article.objects.create(
            title='Test Article two', content='This is a second test article.',
            author=self.user_two,
            approved=True, status='Approved')
        self.article_two.save()

    # test article create api view
    def test_api_article_create(self):
        self.token, created = Token.objects.get_or_create(user=self.user_two)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('eNews:api_article_create')
        data = {
            'title': 'Test Article',
            'content': 'This is a test article.',
            'author': self.user_two.id,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # test unauthorized article create api view
    def test_api_anauthorized(self):
        url = reverse('eNews:api_article_create')
        data = {
            'title': 'Test Article',
            'content': 'This is a test article.',
            'author': self.user_two.id,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # forbidden create article test case
    def test_api_article_create_forbidden(self):
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('eNews:api_article_create')
        data = {
            'title': 'Test Article',
            'content': 'This is a test article.',
            'author': self.user_two.id,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # test article approve api view
    def test_api_article_approved(self):
        self.token, created = Token.objects.get_or_create(user=self.user_three)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        url = reverse('eNews:api_approve_article')
        data = {
                'title': 'Test Article',
                'content': 'This is a test article.',
                'author': self.user_two.id,
                'approved': True, 'status': 'Approved'
                }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # test unauthenticated article approve api view
    def test_api_article_approved_unauthenticated(self):
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('eNews:api_approve_article')
        data = {
                'title': 'Test Article',
                'content': 'This is a test article.',
                'author': self.user_two.id,
                'approved': True, 'status': 'Approved'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # test article subscribers api view
    def test_api_subscribed_reader_articles(self):
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        # subscribe user to journalist
        self.user.subscribed_to_journalists.add(self.journalist)
        self.user.subscribed_to_publishers.add(self.publisher)

        url = reverse('eNews:api_reader_articles')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # test unauthenticated article subscribers api view
    def test_api_subscribed_reader_articles_unauthenticated(self):
        self.token, created = Token.objects.get_or_create(user=self.user_two)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        url = reverse('eNews:api_reader_articles')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # test article update api view
    def test_api_article_update(self):
        self.token, created = Token.objects.get_or_create(user=self.user_three)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        url = reverse('eNews:api_article_detail', args=[self.article.id])
        data = {'title': 'Test Article Updated',
                'author': self.user_two.id}
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Article Updated')

        # test unauthenticated article update api view
    def test_api_article_update_unauthenticated(self):
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        url = reverse('eNews:api_article_detail', args=[self.article.id])
        data = {'title': 'Test Article Updated',
                'author': self.user_two.id}
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # test article delete api view
    def test_api_article_delete(self):
        self.token, created = Token.objects.get_or_create(user=self.user_three)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('eNews:api_article_detail', args=[self.article.id])
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # test unauthenticated article delete api view
    def test_api_article_delete_unauthenticated(self):
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        url = reverse('eNews:api_article_detail', args=[self.article.id])
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# Test if Newsleters function normally
class NewsletterTests(APITestCase):
    def setUp(self):
        """
        Set up test data by creating reader, journalist, and editor users, as well as an approved newsletter.
        This sets up the conditions to test the API views.
        """

        # create reader user
        self.user = User.objects.create_user(
            username='testuser', role='reader', password='testpassword',
            email='testemail@.com', first_name='testfirst', last_name='testlast')

        # create journalist user
        self.user_two = User.objects.create_user(
            username='testuser2', role='journalist', password='testpassword',
            email='testemail02@.com', first_name='testfirst2', last_name='testlast2')

        # create editor user
        self.user_three = User.objects.create_user(
            username='testuser3', role='editor', password='testpassword',
            email='testemail03@.com', first_name='testfirst3', last_name='testlast3')

        # create approved newsletter
        self.newsletter = Newsletter.objects.create(
            title='Test Newsletter', description='This is a test newsletter.', author=self.user_three,
            approved=True, status='Approved')
        self.newsletter.save()

    # test newsletter detail api view
    def test_api_newsletter_detail(self):
        self.token, created = Token.objects.get_or_create(user=self.user_two)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('eNews:api_newsletter_detail', args=[self.newsletter.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # test newsletter create api view
    def test_api_newsletter_create(self):
        self.token, created = Token.objects.get_or_create(user=self.user_two)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('eNews:api_newsletter_create')
        data = {
            'title': 'Test Newsletter',
            'description': 'This is a test newsletter.',
            'author': self.user_two.id,
            'approved': True,
            'status': 'Approved'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # test unauthenticated newsletter create api view
        self.token, created = Token.objects.get_or_create(user=self.user_three)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('eNews:api_newsletter_create')
        data = {
            'title': 'Test Newsletter',
            'description': 'This is a test newsletter.',
            'author': self.user_two.id,
            'approved': True,
            'status': 'Approved'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # test newsletter update api view
    def test_api_newsletter_update(self):
        self.token, created = Token.objects.get_or_create(user=self.user_three)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        url = reverse('eNews:api_newsletter_detail', args=[self.newsletter.id])
        data = {'title': 'Test Newsletter Updated',
                'author': self.user_two.id}
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Newsletter Updated')

    # unauthenticated newsletter update api view
    def test_api_newsletter_update_unauthenticated(self):
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        url = reverse('eNews:api_newsletter_detail', args=[self.newsletter.id])
        data = {'title': 'Test Newsletter Updated',
                'author': self.user_two.id}
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # test newsletter delete api view
    def test_api_newsletter_delete(self):
        self.token, created = Token.objects.get_or_create(user=self.user_three)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('eNews:api_newsletter_detail', args=[self.newsletter.id])
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # test unauthenticated newsletter delete api view
    def test_api_newsletter_delete_unauthenticated(self):
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        url = reverse('eNews:api_newsletter_detail', args=[self.newsletter.id])
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
