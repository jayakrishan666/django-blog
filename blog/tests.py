from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Post, Comment

# Create your tests here.

class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user
        )

    def test_post_str(self):
        self.assertEqual(str(self.post), 'Test Post')

    def test_post_get_absolute_url(self):
        expected_url = reverse('blog:post_detail', kwargs={'pk': self.post.pk})
        self.assertEqual(self.post.get_absolute_url(), expected_url)

class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment'
        )

    def test_comment_str(self):
        self.assertEqual(str(self.comment), 'Test comment...')

class PostListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        for i in range(6):
            Post.objects.create(
                title=f'Test Post {i}',
                content=f'Test content {i}',
                author=self.user
            )

    def test_post_list_view_url(self):
        response = self.client.get(reverse('blog:blogs'))
        self.assertEqual(response.status_code, 200)

    def test_post_list_view_template(self):
        response = self.client.get(reverse('blog:blogs'))
        self.assertTemplateUsed(response, 'blog/post_list.html')

    def test_post_list_pagination(self):
        response = self.client.get(reverse('blog:blogs'))
        self.assertEqual(len(response.context['posts']), 5)
