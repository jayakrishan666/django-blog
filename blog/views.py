from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Post, Comment, Category
from .forms import UserRegistrationForm, PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.utils.text import slugify

def home(request):
    latest_posts = Post.objects.all().order_by('-created_at')[:5]
    categories = Category.objects.all()
    return render(request, 'blog/home.html', {
        'latest_posts': latest_posts,
        'categories': categories
    })

def blogs(request):
    posts = Post.objects.all().order_by('-created_at')
    query = request.GET.get('q')
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__username__icontains=query)
        )
    
    paginator = Paginator(posts, 6)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all().order_by('-created_at')
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('blog:post_detail', pk=pk)
    else:
        comment_form = CommentForm()
    
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form
    })

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Your blog post has been created!')
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, 'You can only edit your own posts.')
        return redirect('blog:post_detail', pk=pk)
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your blog post has been updated!')
            return redirect('blog:post_detail', pk=pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_form.html', {'form': form})

def bloggers(request):
    bloggers = User.objects.filter(post__isnull=False).distinct()
    return render(request, 'blog/blogger_list.html', {'bloggers': bloggers})

def blogger_detail(request, pk):
    blogger = get_object_or_404(User, pk=pk)
    posts = Post.objects.filter(author=blogger).order_by('-created_at')
    return render(request, 'blog/blogger_detail.html', {
        'blogger': blogger,
        'posts': posts
    })

def categories(request):
    categories = Category.objects.all()
    return render(request, 'blog/category_list.html', {'categories': categories})

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category).order_by('-created_at')
    return render(request, 'blog/category_detail.html', {
        'category': category,
        'posts': posts
    })

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'blog/register.html', {'form': form})

class HomeView(ListView):
    template_name = 'blog/home.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Post.objects.all()[:5]

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(author__username__icontains=query)
            )
        return queryset

class CategoryListView(ListView):
    model = Category
    template_name = 'blog/category_list.html'
    context_object_name = 'categories'

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'blog/category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = self.object.posts.all()
        return context

class BloggerListView(ListView):
    model = User
    template_name = 'blog/blogger_list.html'
    context_object_name = 'bloggers'

class BloggerDetailView(DetailView):
    model = User
    template_name = 'blog/blogger_detail.html'
    context_object_name = 'blogger'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(author=self.object)
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        return context

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['content']
    template_name = 'blog/comment_form.html'
    success_url = reverse_lazy('blog:post_detail')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['pk'])
        self.success_url = reverse_lazy('blog:post_detail', kwargs={'pk': self.kwargs['pk']})
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=self.kwargs['pk'])
        return context

@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    # Check if the user is the author of the comment
    if request.user != comment.author:
        return HttpResponseForbidden("You don't have permission to delete this comment.")
    
    post = comment.post
    comment.delete()
    messages.success(request, 'Comment deleted successfully.')
    return redirect('blog:post_detail', pk=post.pk)

from django.shortcuts import render

def post_list(request):
    return render(request, 'blog/post_list.html')  # Ensure this template exists

from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Post

@require_POST
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('blogs')  # Change to the correct name of your blog list view

from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Post, Comment  # Ensure Comment model is imported

from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Post, Comment  # Ensure Comment model is imported

@require_POST
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comment_text = request.POST.get('comment', '').strip()
    
    if comment_text:
        Comment.objects.create(post=post, text=comment_text)

    return redirect('blogs')  # Adjust view name if needed

from django.shortcuts import render
from .models import Blogger  # Ensure Blogger model exists

def blogger_list(request):
    users = User.objects.all()  # Get all users (bloggers)
    return render(request, 'blog/blogger_list.html', {'users': users})

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'blog/category_list.html', {'categories': categories})

from django.shortcuts import render
from .models import Post  # Import the Post model

def post_list(request):
    posts = Post.objects.all()  # Get all posts
    return render(request, 'blog/post_list.html', {'posts': posts})
