from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing, name='landing'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('feed/', views.feed, name='feed'),
    path('profile/', views.profile_view, name='profile'),
    path('post/', views.create_post, name='create_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('dashboard/', views.analytics_dashboard, name='analytics_dashboard'),
    path('api/check-toxic/', views.check_toxic, name='check_toxic'),
    path('api/check-image-toxic/', views.check_image_toxic, name='check_image_toxic'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),



    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('help/', views.help_page, name='help'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
