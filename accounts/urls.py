from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from accounts import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing, name='landing'),
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html'
    ), name='login'),
    path('feed/', views.feed, name='feed'),
    path('chat/<int:user_id>/', views.chat_view, name='chat'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('discover/', views.discover_users, name='discover_users'),
    
    path('profile/', views.profile_view, name='profile'),
    path('post/', views.create_post, name='create_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('dashboard/', views.analytics_dashboard, name='analytics_dashboard'),

    path('accounts/logout/', views.logout_view, name='logout'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('help/', views.help_page, name='help'),

    path('api/check-toxic/', views.check_toxic, name='check_toxic'),
    path('api/check-image-toxic/', views.check_image_toxic, name='check_image_toxic'),
]
