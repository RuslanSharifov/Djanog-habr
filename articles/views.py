from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ArticleForm, RegisterForm
from .models import Article, Category, Dislike, Favorite, Like, Rating


def is_super_admin(user):
    return user.is_authenticated and user.is_superuser


def is_admin(user):
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.groups.filter(name='Admin').exists()
        )
    )


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Registration completed. You can now log in.')
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'articles/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_active:
            login(request, user)
            return redirect('home')

        return render(request, 'articles/login.html', {
            'error': 'Username, password, or account status is invalid.'
        })

    return render(request, 'articles/login.html')


def user_logout(request):
    logout(request)
    return redirect('login')


def home(request):
    articles = Article.objects.filter(
        is_published=True
    ).select_related(
        'category',
        'author'
    ).annotate(
        average_rating=Avg('rating__value'),
        like_count=Count('like', distinct=True),
    ).order_by('-created_at')

    categories = Category.objects.all()

    popular_articles = Article.objects.filter(
        is_published=True
    ).annotate(
        average_rating=Avg('rating__value')
    ).filter(
        average_rating__gte=4
    ).order_by(
        '-average_rating'
    )[:5]

    return render(request, 'articles/home.html', {
        'articles': articles,
        'categories': categories,
        'popular_articles': popular_articles,
    })


def article_detail(request, article_id):
    article = get_object_or_404(
        Article.objects.select_related('author', 'category').annotate(
            average_rating=Avg('rating__value'),
            like_count=Count('like', distinct=True),
            dislike_count=Count('dislike', distinct=True),
            favorite_count=Count('favorite', distinct=True),
            rating_count=Count('rating', distinct=True),
        ),
        id=article_id
    )

    if not article.is_published:
        if not request.user.is_authenticated or (
            request.user != article.author and not is_admin(request.user)
        ):
            return get_object_or_404(Article, id=article_id, is_published=True)

    user_rating = None
    user_liked = False
    user_disliked = False
    user_favorite = False

    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(
            user=request.user,
            article=article
        ).values_list('value', flat=True).first()

        user_liked = Like.objects.filter(
            user=request.user,
            article=article
        ).exists()

        user_disliked = Dislike.objects.filter(
            user=request.user,
            article=article
        ).exists()

        user_favorite = Favorite.objects.filter(
            user=request.user,
            article=article
        ).exists()

    return render(request, 'articles/article_detail.html', {
        'article': article,
        'user_rating': user_rating,
        'user_liked': user_liked,
        'user_disliked': user_disliked,
        'user_favorite': user_favorite,
    })


@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)

        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.is_published = False
            article.save()

            messages.success(
                request,
                'Article submitted successfully. It is waiting for admin approval.'
            )
            return redirect('article_detail', article.id)
    else:
        form = ArticleForm()

    return render(request, 'articles/article_create.html', {'form': form})


@login_required
def article_edit(request, article_id):
    article = get_object_or_404(
        Article,
        id=article_id,
        author=request.user
    )

    if request.method == 'POST':
        form = ArticleForm(
            request.POST,
            request.FILES,
            instance=article
        )

        if form.is_valid():
            article = form.save(commit=False)
            article.is_published = False
            article.save()

            messages.success(
                request,
                'Article updated and sent for approval again.'
            )
            return redirect('article_detail', article.id)
    else:
        form = ArticleForm(instance=article)

    return render(request, 'articles/article_create.html', {
        'form': form,
        'article': article,
        'is_edit': True,
    })


@login_required
def article_delete(request, article_id):
    article = get_object_or_404(
        Article,
        id=article_id,
        author=request.user
    )

    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Article deleted.')
        return redirect('home')

    return redirect('article_detail', article_id)


def popular(request):
    articles = Article.objects.filter(
        is_published=True
    ).annotate(
        average_rating=Avg('rating__value')
    ).filter(
        average_rating__gte=4
    ).order_by('-average_rating')

    return render(request, 'articles/popular.html', {'articles': articles})


def categories(request):
    categories = Category.objects.all()
    return render(request, 'articles/categories.html', {'categories': categories})


def category_articles(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    articles = Article.objects.filter(
        category=category,
        is_published=True
    ).order_by('-created_at')

    return render(request, 'articles/category_articles.html', {
        'category': category,
        'articles': articles
    })


def authors(request):
    author_ids = Article.objects.filter(
        is_published=True
    ).values_list(
        'author',
        flat=True
    ).distinct()

    authors = User.objects.filter(id__in=author_ids)

    return render(request, 'articles/authors.html', {'authors': authors})


def author_articles(request, author_id):
    author = get_object_or_404(User, id=author_id)

    articles = Article.objects.filter(
        author=author,
        is_published=True
    ).order_by('-created_at')

    return render(request, 'articles/author_articles.html', {
        'author': author,
        'articles': articles
    })


@login_required
def favorites(request):
    favorite_articles = Favorite.objects.filter(
        user=request.user,
        article__is_published=True
    ).select_related('article', 'article__author', 'article__category')

    return render(request, 'articles/favorites.html', {
        'favorites': favorite_articles
    })


@login_required
def article_like(request, article_id):
    article = get_object_or_404(
        Article,
        id=article_id,
        is_published=True
    )

    if Like.objects.filter(user=request.user, article=article).exists():
        Like.objects.filter(user=request.user, article=article).delete()
    else:
        Like.objects.get_or_create(user=request.user, article=article)
        Dislike.objects.filter(
            user=request.user,
            article=article
        ).delete()

    return redirect('article_detail', article_id)


@login_required
def article_dislike(request, article_id):
    article = get_object_or_404(
        Article,
        id=article_id,
        is_published=True
    )

    if Dislike.objects.filter(user=request.user, article=article).exists():
        Dislike.objects.filter(
            user=request.user,
            article=article
        ).delete()
    else:
        Dislike.objects.get_or_create(user=request.user, article=article)
        Like.objects.filter(
            user=request.user,
            article=article
        ).delete()

    return redirect('article_detail', article_id)


@login_required
def article_rate(request, article_id):
    article = get_object_or_404(
        Article,
        id=article_id,
        is_published=True
    )

    if request.method == 'POST':
        try:
            value = int(request.POST.get('value', 0))
        except (TypeError, ValueError):
            value = 0

        if value < 1 or value > 5:
            messages.error(request, 'Rating must be between 1 and 5.')
        else:
            Rating.objects.update_or_create(
                user=request.user,
                article=article,
                defaults={'value': value}
            )
            messages.success(request, 'Your rating has been saved.')

    return redirect('article_detail', article_id)


@login_required
def article_favorite(request, article_id):
    article = get_object_or_404(
        Article,
        id=article_id,
        is_published=True
    )

    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        article=article
    )

    if not created:
        favorite.delete()
        messages.success(request, 'Article removed from favorites.')
    else:
        messages.success(request, 'Article added to favorites.')

    return redirect('article_detail', article_id)


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    pending_articles = Article.objects.filter(
        is_published=False
    ).select_related(
        'author',
        'category'
    ).order_by('-created_at')

    users_count = User.objects.count()
    blocked_count = User.objects.filter(is_active=False).count()
    admin_count = User.objects.filter(groups__name='Admin').distinct().count()

    return render(request, 'articles/admin_dashboard.html', {
        'pending_articles': pending_articles,
        'users_count': users_count,
        'blocked_count': blocked_count,
        'admin_count': admin_count,
        'is_super_admin': is_super_admin(request.user),
    })


@login_required
@user_passes_test(is_admin)
def approve_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    if request.method == 'POST':
        article.is_published = True
        article.save(update_fields=['is_published', 'updated_at'])
        messages.success(request, f'Article "{article.title}" approved.')

    return redirect('admin_dashboard')


@login_required
@user_passes_test(is_admin)
def reject_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    if request.method == 'POST':
        article.is_published = False
        article.save(update_fields=['is_published', 'updated_at'])
        messages.success(
            request,
            f'Article "{article.title}" remains unpublished.'
        )

    return redirect('admin_dashboard')


@login_required
@user_passes_test(is_admin)
def admin_users(request):
    users = User.objects.all().prefetch_related('groups').order_by(
        '-date_joined'
    )

    return render(request, 'articles/admin_users.html', {
        'users': users,
        'is_super_admin': is_super_admin(request.user),
    })


@login_required
@user_passes_test(is_admin)
def toggle_user_block(request, user_id):
    target = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        if target.is_superuser:
            messages.error(request, 'Super Admin cannot be blocked.')
        elif target == request.user:
            messages.error(request, 'You cannot block your own account.')
        elif target.groups.filter(name='Admin').exists() and not is_super_admin(request.user):
            messages.error(request, 'Only Super Admin can block an Admin.')
        else:
            target.is_active = not target.is_active
            target.save(update_fields=['is_active'])
            status = 'blocked' if not target.is_active else 'unblocked'
            messages.success(
                request,
                f'User {target.username} has been {status}.'
            )

    return redirect('admin_users')


@login_required
@user_passes_test(is_super_admin)
def assign_admin(request, user_id):
    target = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        target.groups.add(admin_group)
        messages.success(
            request,
            f'{target.username} is now an Admin.'
        )

    return redirect('admin_users')


@login_required
@user_passes_test(is_super_admin)
def remove_admin(request, user_id):
    target = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        target.groups.filter(name='Admin').delete()
        messages.success(
            request,
            f'{target.username} is no longer an Admin.'
        )

    return redirect('admin_users')
