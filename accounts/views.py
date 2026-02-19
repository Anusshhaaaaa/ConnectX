from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Q, Count
from datetime import datetime, timedelta
import json

from .models import Post, Comment, ContentAnalytics
from .utils import detect_toxic_content, get_safer_alternative, analyze_image_toxicity


# ============================================
# KEYWORD OVERRIDE LAYER
# ============================================

TOXIC_THRESHOLD = 0.5

hard_block_words = ["idiot", "stupid", "moron", "kill"]
soft_boost_words = ["trash", "nonsense", "useless"]
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
        insult_patterns = [
            f"you are {word}",
            f"u r {word}",
            f"you're {word}",
            f"ur {word}"
        ]
        for pattern in insult_patterns:
            if pattern in text_lower:
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
    posts = Post.objects.all()

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
@require_http_methods(["GET", "POST"])
def create_post(request):

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')

        if not content and not image:
            return render(request, 'accounts/create_post.html', {
                'error': 'Post cannot be empty'
            })

        # =========================
        # TEXT TOXICITY CHECK
        # =========================
        is_toxic = False
        toxic_score = 0

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
                is_toxic = True
                toxic_score = max(toxic_score, 0.75)

            if is_toxic:
                safer_alternative = get_safer_alternative(content, is_toxic)

                return render(request, 'accounts/create_post.html', {
                    'error': 'Toxic text detected. Please revise your message.',
                    'original_content': content,
                    'toxicity_score': round(toxic_score, 2),
                    'safer_alternative': safer_alternative
                })

        # =========================
        # IMAGE TOXICITY CHECK
        # =========================
        if image:
            image_result = analyze_image_toxicity(image)

            if image_result.get("is_toxic"):
                return render(request, 'accounts/create_post.html', {
                    'error': 'Toxic image detected. Please upload a safe image.',
                    'image_feedback': image_result.get("reason"),
                    'original_content': content,
                    'toxicity_score': toxic_score
                })

        # =========================
        # CREATE POST
        # =========================
        Post.objects.create(
            author=request.user,
            content=content,
            image=image,
            is_toxic=False,
            toxic_score=toxic_score
        )

        update_analytics()
        return redirect('feed')

    return render(request, 'accounts/create_post.html')


@login_required(login_url='login')
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return redirect('feed')

    post.delete()
    update_analytics()
    return redirect('feed')


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
        is_toxic = True
        toxic_score = max(toxic_score, 0.75)

    if is_toxic:
        return redirect('feed')  # You can later improve UX here

    # =========================
    # CREATE COMMENT
    # =========================
    Comment.objects.create(
        post=post,
        author=request.user,
        content=content,
        is_toxic=False,
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
# ANALYTICS
# ============================================

@login_required(login_url='login')
def analytics_dashboard(request):

    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    analytics_data = ContentAnalytics.objects.filter(date__gte=thirty_days_ago).order_by('date')

    total_posts = Post.objects.count()
    toxic_posts = Post.objects.filter(is_toxic=True).count()
    safe_posts = total_posts - toxic_posts

    avg_toxic = Post.objects.filter(is_toxic=True).values_list('toxic_score', flat=True)
    avg_toxic_score = sum(avg_toxic) / len(avg_toxic) if avg_toxic else 0

    return render(request, 'accounts/dashboard.html', {
        'total_posts': total_posts,
        'toxic_posts': toxic_posts,
        'safe_posts': safe_posts,
        'avg_toxic_score': round(avg_toxic_score, 2),
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
    analytics.total_safe_posts = analytics.total_posts - analytics.total_toxic_posts

    toxic_posts = Post.objects.filter(is_toxic=True).values_list('toxic_score', flat=True)
    analytics.avg_toxic_score = sum(toxic_posts) / len(toxic_posts) if toxic_posts else 0

    analytics.save()

# ============================================
# API ENDPOINT: CHECK TOXIC (AJAX)
# ============================================

@login_required(login_url='login')
@require_http_methods(["POST"])
def check_toxic(request):
    try:
        data = json.loads(request.body)
        content = data.get('content', '')

        is_toxic, toxic_score = detect_toxic_content(content)
        override_result = keyword_override_check(content)

        if override_result == "hard_block":
            is_toxic = True
            toxic_score = max(toxic_score, 0.9)

        elif override_result == "safe_override":
            is_toxic = False
            toxic_score = 0

        elif override_result == "soft_boost":
            is_toxic = True
            toxic_score = max(toxic_score, 0.75)

        safer_alternative = (
            get_safer_alternative(content, is_toxic)
            if is_toxic else None
        )

        return JsonResponse({
            'is_toxic': is_toxic,
            'toxicity_score': round(toxic_score, 2),
            'safer_alternative': safer_alternative,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

