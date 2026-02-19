from django.db import models
from django.contrib.auth.models import User
from accounts.utils import process_user_post


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')

    content = models.TextField(blank=True, null=True)
    safer_content = models.TextField(blank=True, null=True)

    image = models.ImageField(upload_to="post_images/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    is_toxic = models.BooleanField(default=False)
    toxic_score = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def like_count(self):
        return self.likes.count()

    def save(self, *args, **kwargs):
        if self.content:
            result = process_user_post(self.content)
            self.safer_content = result['safer_text']
            self.is_toxic = result['is_toxic']
            self.toxic_score = result['toxicity_score']
        super().save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_toxic = models.BooleanField(default=False)
    toxic_score = models.FloatField(default=0.0)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post}"


class ContentAnalytics(models.Model):
    date = models.DateField(auto_now_add=True, unique=True)
    total_posts = models.IntegerField(default=0)
    total_toxic_posts = models.IntegerField(default=0)
    total_safe_posts = models.IntegerField(default=0)
    text_posts = models.IntegerField(default=0)
    image_posts = models.IntegerField(default=0)
    avg_toxic_score = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Analytics for {self.date}"
