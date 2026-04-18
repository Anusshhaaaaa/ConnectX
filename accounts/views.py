from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Profile
import json

from .models import Post, Comment, ContentAnalytics
from .utils import detect_toxic_content, get_safer_alternative, analyze_image_toxicity


# ============================================
# KEYWORD OVERRIDE LAYER
# ============================================

import re

hard_block_words = ["idiot", "stupid", "moron", "kill","nonsense",]
soft_boost_words = ["trash", "ridiculous", "useless", "worthless", "disgusting"]
safe_override_words = ["kill process", "execute command"]


def keyword_override_check(text):
    text_lower = text.lower()

    for word in hard_block_words:
        if word in text_lower:
            return "hard_block"

    for phrase in safe_override_words:
        if phrase in text_lower:
            return "safe_override"

    for word in soft_boost_words:
        pattern = rf"\b(u|you|ur|you\'re)\s*(are|r)?\s*(a\s*)?{re.escape(word)}\b"
        if re.search(pattern, text_lower):
            return "soft_boost"

    return "none"



# ============================================
# AUTHENTICATION VIEWS
# ============================================

def landing(request):
    if request.user.is_authenticated:
        return redirect('feed')
    return render(request, 'accounts/landing.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('feed')
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('landing')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(request, 'accounts/register.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/register.html', {'error': 'Username already exists'})

        if User.objects.filter(email=email).exists():
            return render(request, 'accounts/register.html', {'error': 'Email already exists'})

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('feed')

    return render(request, 'accounts/register.html')


# ============================================
# FEED & POST VIEWS
# ============================================

@login_required(login_url='login')
def feed(request):
    if not hasattr(request.user, 'profile'):
        Profile.objects.get_or_create(user=request.user)
    profile = request.user.profile
    posts = Post.objects.exclude(author=request.user)

    search_query = request.GET.get('search', '')
    if search_query:
        posts = posts.filter(
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )

    content_type = request.GET.get('type', '')
    if content_type == 'text':
        posts = posts.filter(image__isnull=True)
    elif content_type == 'image':
        posts = posts.filter(image__isnull=False)

    posts = posts.annotate(like_count=Count('likes'))

    return render(request, 'accounts/feed.html', {
        'posts': posts,
        'search_query': search_query,
        'content_type': content_type,
    })


@login_required(login_url='login')
def profile_view(request):
    if not hasattr(request.user, 'profile'):
        Profile.objects.get_or_create(user=request.user)
    profile = request.user.profile
    
    own_posts = Post.objects.filter(author=request.user).annotate(
        like_count=Count('likes')
    ).order_by('-created_at')
    
    stats = {
        'posts': own_posts.count(),
        'followers': profile.following.through.objects.filter(user__id=profile.user.id).count(),
        'following': profile.following.count(),
    }
    
    # Global analytics data (keep existing)
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    analytics_data = ContentAnalytics.objects.filter(date__gte=thirty_days_ago).order_by('date')

    total_posts = Post.objects.count()
    toxic_posts = Post.objects.filter(is_toxic=True).count()

    safe_posts = Post.objects.filter(originally_toxic=False).count()

    avg_toxic_list = list(Post.objects.filter(is_toxic=True).values_list('toxic_score', flat=True))
    avg_toxic_score = sum(avg_toxic_list) / len(avg_toxic_list) if avg_toxic_list else 0

    safe_percentage = (safe_posts / total_posts * 100) if total_posts > 0 else 0
    toxic_percentage = 100 - safe_percentage

    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'own_posts': own_posts,
        'stats': stats,
        'total_posts': total_posts,
        'toxic_posts': toxic_posts,

        'safe_posts': safe_posts,
        'avg_toxic_score': round(avg_toxic_score, 2),
        'safe_percentage': round(safe_percentage, 1),
        'toxic_percentage': round(toxic_percentage, 1),
        'analytics_data': analytics_data,
    })


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def create_post(request):

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')

        if not content and not image:
            return render(request, 'accounts/create_post_fixed.html', {
                'error': 'Post cannot be empty'
            })

        # Step 1: Check toxicity via API
        is_toxic = False
        toxic_score = 0.0

        if content:
            is_toxic, toxic_score = detect_toxic_content(content)
            override_result = keyword_override_check(content)

            if override_result == "hard_block":
                is_toxic = True
                toxic_score = max(toxic_score, 0.9)

            elif override_result == "safe_override":
                is_toxic = False
                toxic_score = 0

            elif override_result == "soft_boost":
                toxic_score = max(toxic_score, 0.75)
                is_toxic = toxic_score > 0.5

        # IMAGE TOXICITY CHECK (BLOCKING)
        if image:
            image_result = analyze_image_toxicity(image)
            if image_result["is_toxic"]:
                return render(request, "accounts/create_post_fixed.html", {
                    "error": image_result["reason"]
                })

        # Step 2: Create post object
        post = Post.objects.create(
            author=request.user,
            content=content,
            image=image,
            originally_toxic=is_toxic,
            toxic_score=toxic_score
        )

        # Step 3: Optionally rewrite toxic content
        if is_toxic:
            post.safer_content = get_safer_alternative(content, is_toxic)
            post.save()  # triggers model logic: originally_toxic → is_toxic



        update_analytics()
        return redirect('profile')

    return render(request, 'accounts/create_post_fixed.html', {})


@login_required(login_url='login')
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.delete()
    return redirect('profile')


@login_required(login_url='login')
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    return redirect('feed')

# ============================================
# COMMENT VIEW
# ============================================

@login_required(login_url='login')
@require_http_methods(["POST"])
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    content = request.POST.get('content', '').strip()

    if not content:
        return redirect('feed')

    # =========================
    # TEXT TOXICITY CHECK
    # =========================
    is_toxic, toxic_score = detect_toxic_content(content)
    override_result = keyword_override_check(content)

    if override_result == "hard_block":
        is_toxic = True
        toxic_score = max(toxic_score, 0.9)

    elif override_result == "safe_override":
        is_toxic = False
        toxic_score = 0

    elif override_result == "soft_boost":
        toxic_score = max(toxic_score, 0.75)
        is_toxic = toxic_score > 0.5

    # =========================
    # CREATE COMMENT (NO BLOCKING)
    # =========================
    Comment.objects.create(
        post=post,
        author=request.user,
        content=content,
        is_toxic=is_toxic,   # 🔥 now dynamic
        toxic_score=toxic_score
    )

    return redirect('feed')

# ============================================
# CHAT VIEW
# ============================================

@login_required(login_url='login')
def chat_view(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    return render(request, 'accounts/chat.html', {'receiver': receiver})


# ============================================
# ANALYTICS DASHBOARD
# ============================================

@login_required(login_url='login')
def analytics_dashboard(request):
    if not hasattr(request.user, 'profile'):
        Profile.objects.get_or_create(user=request.user)
    
    # Global analytics data - 30 days filter
    thirty_days_ago = timezone.now() - timedelta(days=30)
    analytics_data = ContentAnalytics.objects.filter(date__gte=thirty_days_ago).order_by('date')

    # Posts - Last 30 days
    post_qs = Post.objects.filter(created_at__gte=thirty_days_ago)
    total_posts = post_qs.count()
    toxic_posts = post_qs.filter(is_toxic=True).count()
    safe_posts = post_qs.filter(originally_toxic=False).count()
    text_posts = post_qs.filter(Q(image__isnull=True) | Q(image__exact='')).count()
    image_posts = total_posts - text_posts
    avg_toxic_posts = post_qs.filter(is_toxic=True).aggregate(avg=Avg('toxic_score'))['avg'] or 0.0

    safe_percentage = (safe_posts / total_posts * 100) if total_posts > 0 else 0
    toxic_percentage = 100 - safe_percentage

    # Top users by post count
    top_users = (User.objects
                 .annotate(post_count=Count('posts'))
                 .order_by('-post_count')[:5])

    # Comments - Last 30 days
    comment_qs = Comment.objects.filter(created_at__gte=thirty_days_ago)
    total_comments = comment_qs.count()
    safe_comments = comment_qs.filter(originally_toxic=False).count()
    toxic_comments = comment_qs.filter(is_toxic=True).count()
    avg_toxic_comments = comment_qs.filter(is_toxic=True).aggregate(avg=Avg('toxic_score'))['avg'] or 0.0
    safe_pct_comments = (safe_comments / total_comments * 100) if total_comments else 0
    safe_pct_posts = round(safe_percentage, 1)
    safe_pct_comments = round(safe_pct_comments, 1)
    toxic_pct_comments = 100 - safe_pct_comments
    overall_health_score = (safe_pct_posts + safe_pct_comments) / 2

    # Top posters and commenters (30 days)
    top_posters = User.objects.filter(posts__created_at__gte=thirty_days_ago).annotate(
        post_count=Count('posts')
    ).order_by('-post_count')[:5]
    top_commenters = User.objects.filter(comment__created_at__gte=thirty_days_ago).annotate(
        comment_count=Count('comment')
    ).order_by('-comment_count')[:5]

    return render(request, 'accounts/dashboard.html', {
        'total_posts': total_posts,
        'toxic_posts': toxic_posts,
        'safe_posts': safe_posts,
        'text_posts': text_posts,
        'image_posts': image_posts,
        'avg_toxic_posts': round(avg_toxic_posts, 2),
        'safe_pct_posts': round(safe_percentage, 1),
        'toxic_pct_posts': round(toxic_percentage, 1),

        'total_comments': total_comments,
        'toxic_comments': toxic_comments,
        'safe_comments': safe_comments,
        'avg_toxic_comments': round(avg_toxic_comments, 2),
        'safe_pct_comments': round(safe_pct_comments, 1),
'toxic_pct_comments': round(toxic_pct_comments, 1),
        'overall_health_score': round(overall_health_score, 1),

        'top_posters': top_posters,
        'top_commenters': top_commenters,
        'analytics_data': analytics_data,
    })


# ============================================
# UTILITIES
# ============================================

def update_analytics():
    today = datetime.now().date()
    analytics, created = ContentAnalytics.objects.get_or_create(date=today)

    analytics.total_posts = Post.objects.count()
    analytics.total_toxic_posts = Post.objects.filter(is_toxic=True).count()
    analytics.originally_toxic_posts = Post.objects.filter(originally_toxic=True).count()
    analytics.rephrased_posts = Post.objects.filter(originally_toxic=True, is_toxic=False).count()
    analytics.total_safe_posts = Post.objects.filter(originally_toxic=False).count()

    toxic_posts = Post.objects.filter(is_toxic=True).values_list('toxic_score', flat=True)
    analytics.avg_toxic_score = sum(toxic_posts) / len(toxic_posts) if toxic_posts else 0

    analytics.save()


# ============================================
# API ENDPOINT: CHECK TOXIC (AJAX)
# ============================================

@login_required(login_url='login')
@require_http_methods(["POST"])
def check_toxic(request):
    if not request.body:
        return JsonResponse({"error": "Empty body"}, status=400)

    try:
        data = json.loads(request.body.decode("utf-8"))
        content = data.get("content", "").strip()

        if not content:
            return JsonResponse({"error": "Empty content"}, status=400)

        is_toxic, toxic_score = detect_toxic_content(content)
        override_result = keyword_override_check(content)

        if override_result == "hard_block":
            is_toxic = True
            toxic_score = max(toxic_score, 0.9)

        elif override_result == "safe_override":
            is_toxic = False
            toxic_score = 0

        elif override_result == "soft_boost":
            toxic_score = max(toxic_score, 0.75)
            is_toxic = toxic_score > 0.5

        safer_alternative = None

        return JsonResponse({
            'is_toxic': bool(is_toxic),
            'toxicity_score': float(round(toxic_score, 2)),
        })


    except Exception as e:
        print("JSON ERROR:", e)
        return JsonResponse({'error': "Invalid JSON"}, status=400)

# ============================================
# API ENDPOINT: CHECK IMAGE TOXIC (AJAX)
# ============================================

@login_required(login_url='login')
@require_http_methods(["POST"])
def check_image_toxic(request):
    """
    AJAX endpoint to check image toxicity before previewing.
    Expects FormData with 'image' file.
    """
    try:
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image file provided'}, status=400)
        
        image = request.FILES['image']
        result = analyze_image_toxicity(image)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# your existing views above...
@login_required(login_url='login')
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    if not request.user.profile.following.filter(id=user_id).exists():
        request.user.profile.following.add(user_to_follow)
    followers_count = user_to_follow.followers.count()
    following_count = request.user.profile.following.count()
    return JsonResponse({
        "status": "followed",
        "followers_count": followers_count,
        "following_count": following_count
    })
    
@login_required(login_url='login')
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    if request.user.profile.following.filter(id=user_id).exists():
        request.user.profile.following.remove(user_to_unfollow)
    followers_count = user_to_unfollow.followers.count()
    following_count = request.user.profile.following.count()
    return JsonResponse({
        "status": "unfollowed",
        "followers_count": followers_count,
        "following_count": following_count
    })

@login_required(login_url='login')
def discover_users(request):

    users = User.objects.exclude(id=request.user.id)

    return render(request, 'accounts/discover.html', {
        'users': users
    })

@login_required(login_url='login')
def edit_profile(request):
    """Stub for edit profile form - to be implemented"""
    return render(request, 'accounts/edit_profile.html', {'user': request.user})

@login_required(login_url='login')
def help_page(request):
    """Help/Support page - to be implemented""" 
    return render(request, 'accounts/help.html')
