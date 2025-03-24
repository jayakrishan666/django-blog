from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name_plural = 'categories'

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='posts', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['-created_at']

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.content[:75]}..."

    class Meta:
        ordering = ['created_at']

class Blogger(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()


from django.db import models

class Blogger(models.Model):
    username = models.CharField(max_length=150, unique=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.username
