from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg

from .forms import RegisterForm, ArticleForm
from .models import (
    Article,
    Category,
    Favorite,
    Like,
    Dislike
)

from .decorators import (
    admin_required,
    super_admin_required,
    get_admin_group
)



def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'articles/register.html', {
        'form': form
    })


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('home')

        return render(request, 'articles/login.html', {
            'error': 'Username və ya password yanlışdır.'
        })

    return render(request, 'articles/login.html')


def user_logout(request):
    logout(request)
    return redirect('login')


@admin_required
def management(request):
    articles = Article.objects.filter(
        author__isnull=False
    ).select_related(
        'author',
        'category'
    ).order_by('-created_at')

    users = User.objects.all().order_by('username')

    return render(
        request,
        'articles/management.html',
        {
            'articles': articles,
            'users': users,
        }
    )


@super_admin_required
def admin_management(request):
    users = User.objects.all().order_by(
        'username'
    )

    admin_group = get_admin_group()

    user_data = []

    for user in users:
        user_data.append({
            'user': user,
            'is_admin': admin_group in user.groups.all(),
        })

    return render(request, 'articles/admin_management.html', {
        'user_data': user_data,
    })


@super_admin_required
def make_admin(request, user_id):
    user = get_object_or_404(
        User,
        id=user_id
    )

    if user.is_superuser:
        return redirect('admin_management')

    admin_group = get_admin_group()

    user.groups.add(admin_group)

    return redirect('admin_management')


@super_admin_required
def remove_admin(request, user_id):
    user = get_object_or_404(
        User,
        id=user_id
    )

    if user.is_superuser:
        return redirect('admin_management')

    admin_group = get_admin_group()

    user.groups.remove(admin_group)

    return redirect('admin_management')


def home(request):
    articles = Article.objects.filter(
        is_published=True
    ).select_related(
        'category',
        'author'
    ).order_by('-created_at')

    categories = Category.objects.all()

    popular_articles = Article.objects.filter(
        is_published=True
    ).annotate(
        average_rating=Avg('rating__value')
    ).filter(
        average_rating__gte=4
    ).order_by('-average_rating')[:5]

    for article in articles:
        article.like_count = Like.objects.filter(
            article=article
        ).count()

        article.dislike_count = Dislike.objects.filter(
            article=article
        ).count()

        article.favorite_count = Favorite.objects.filter(
            article=article
        ).count()

        article.is_liked = False
        article.is_disliked = False
        article.is_favorite = False

        if request.user.is_authenticated:
            article.is_liked = Like.objects.filter(
                user=request.user,
                article=article
            ).exists()

            article.is_disliked = Dislike.objects.filter(
                user=request.user,
                article=article
            ).exists()

            article.is_favorite = Favorite.objects.filter(
                user=request.user,
                article=article
            ).exists()

    return render(request, 'articles/home.html', {
        'articles': articles,
        'categories': categories,
        'popular_articles': popular_articles,
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

            return redirect('home')
    else:
        form = ArticleForm()

    return render(request, 'articles/article_create.html', {
        'form': form
    })


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

            # Edit olunan məqalə yenidən approval gözləyir
            article.is_published = False
            article.save()

            return redirect('article_detail', article.id)
    else:
        form = ArticleForm(instance=article)

    return render(request, 'articles/article_edit.html', {
        'form': form
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
        return redirect('home')

    return render(request, 'articles/article_detail.html', {
        'article': article
    })


def popular(request):
    articles = Article.objects.filter(
        is_published=True
    ).annotate(
        average_rating=Avg('rating__value')
    ).filter(
        average_rating__gte=4
    ).order_by('-average_rating')

    return render(request, 'articles/popular.html', {
        'articles': articles
    })


def categories(request):
    categories = Category.objects.all()

    return render(request, 'articles/categories.html', {
        'categories': categories
    })


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
    authors = Article.objects.filter(
        is_published=True
    ).values_list(
        'author',
        flat=True
    ).distinct()

    from django.contrib.auth.models import User

    authors = User.objects.filter(id__in=authors)

    return render(request, 'articles/authors.html', {
        'authors': authors
    })


def author_articles(request, author_id):
    from django.contrib.auth.models import User

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
def article_detail(request, article_id):
    article = Article.objects.filter(
        id=article_id
    ).select_related(
        'author',
        'category'
    ).first()

    if (
        article is None
        or (
            not article.is_published
            and not (
                request.user.is_superuser
                or request.user.groups.filter(name='Admin').exists()
                or article.author_id == request.user.id
            )
        )
    ):
        return render(request, 'articles/article_not_found.html')

    is_liked = Like.objects.filter(
        user=request.user,
        article=article
    ).exists()

    is_disliked = Dislike.objects.filter(
        user=request.user,
        article=article
    ).exists()

    is_favorite = Favorite.objects.filter(
        user=request.user,
        article=article
    ).exists()

    like_count = Like.objects.filter(article=article).count()
    dislike_count = Dislike.objects.filter(article=article).count()
    favorite_count = Favorite.objects.filter(article=article).count()

    return render(request, 'articles/article_detail.html', {
        'article': article,
        'is_liked': is_liked,
        'is_disliked': is_disliked,
        'is_favorite': is_favorite,
        'like_count': like_count,
        'dislike_count': dislike_count,
        'favorite_count': favorite_count,
    })


@login_required
def article_like(request, article_id):
    article = get_object_or_404(
        Article,
        id=article_id
    )

    Like.objects.get_or_create(
        user=request.user,
        article=article
    )

    Dislike.objects.filter(
        user=request.user,
        article=article
    ).delete()

    if request.POST.get('next') == 'home':
        return redirect('home')

    return redirect(
        'article_detail',
        article_id=article_id
    )


@login_required
def article_dislike(request, article_id):
    article = get_object_or_404(
        Article,
        id=article_id
    )

    Dislike.objects.get_or_create(
        user=request.user,
        article=article
    )

    Like.objects.filter(
        user=request.user,
        article=article
    ).delete()

    if request.POST.get('next') == 'home':
        return redirect('home')

    return redirect(
        'article_detail',
        article_id=article_id
    )


@login_required
def article_favorite(request, article_id):
    article = get_object_or_404(
        Article,
        id=article_id
    )

    favorite = Favorite.objects.filter(
        user=request.user,
        article=article
    ).first()

    if favorite:
        favorite.delete()
    else:
        Favorite.objects.create(
            user=request.user,
            article=article
        )

    if request.POST.get('next') == 'home':
        return redirect('home')

    return redirect(
        'article_detail',
        article_id=article_id
    )


@login_required
def favorites(request):
    favorites = Favorite.objects.filter(
        user=request.user,
        article__is_published=True
    ).select_related(
        'article',
        'article__author',
        'article__category'
    ).order_by('-id')

    return render(
        request,
        'articles/favorites.html',
        {
            'favorites': favorites
        }
    )


@login_required
@admin_required
def toggle_article_publish(request, article_id):
    article = get_object_or_404(
        Article,
        id=article_id
    )

    article.is_published = not article.is_published
    article.save(update_fields=['is_published', 'updated_at'])

    return redirect('management')