from django.contrib import admin
from .models import Post, Comment, Category

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'author', 'category')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'
    inlines = [CommentInline]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('content',)
    date_hierarchy = 'created_at'
