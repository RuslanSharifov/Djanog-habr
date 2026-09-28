from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Avg

from .forms import RegisterForm, ArticleForm
from .models import (
    Article,
    Category,
    Favorite,
    Like,
    Dislike
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


def home(request):
    articles = Article.objects.filter(
        is_published=True
    ).select_related(
        'category'
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
        Article,
        id=article_id,
        is_published=True
    )

    return render(request, 'articles/article_detail.html', {
        'article': article
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
def favorites(request):
    favorites = Favorite.objects.filter(
        user=request.user,
        article__is_published=True
    ).select_related('article')

    return render(request, 'articles/favorites.html', {
        'favorites': favorites
    })

@login_required
def article_like(request, article_id):
    article = get_object_or_404(
        Article,
        id=article_id,
        is_published=True
    )

    Like.objects.get_or_create(
        user=request.user,
        article=article
    )

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

    Dislike.objects.get_or_create(
        user=request.user,
        article=article
    )

    Like.objects.filter(
        user=request.user,
        article=article
    ).delete()

    return redirect('article_detail', article_id)