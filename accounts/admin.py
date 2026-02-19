from django.contrib import admin
from .models import Post, Comment, ContentAnalytics

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'created_at', 'is_toxic', 'toxic_score', 'like_count']
    list_filter = ['is_toxic', 'created_at']
    search_fields = ['author__username', 'content']
    readonly_fields = ['created_at', 'updated_at', 'toxic_score']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at', 'is_toxic']
    list_filter = ['is_toxic', 'created_at']
    search_fields = ['author__username', 'content']

@admin.register(ContentAnalytics)
class ContentAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_posts', 'total_toxic_posts', 'total_safe_posts', 'avg_toxic_score']
    list_filter = ['date']
    readonly_fields = ['date']

