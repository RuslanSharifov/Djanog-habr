from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),

    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path(
        'article/<int:article_id>/',
        views.article_detail,
        name='article_detail'
    ),

    path(
        'article/create/',
        views.article_create,
        name='article_create'
    ),

    path(
        'article/<int:article_id>/like/',
        views.article_like,
        name='article_like'
    ),

    path(
        'article/<int:article_id>/dislike/',
        views.article_dislike,
        name='article_dislike'
    ),

    path(
        'article/<int:article_id>/edit/',
        views.article_edit,
        name='article_edit'
    ),

    path(
        'article/<int:article_id>/delete/',
        views.article_delete,
        name='article_delete'
    ),


    path(
        'article/<int:article_id>/favorite/',
        views.article_favorite,
        name='article_favorite'
    ),

    path(
        'popular/',
        views.popular,
        name='popular'
    ),

    path(
        'categories/',
        views.categories,
        name='categories'
    ),

    path(
        'categories/<int:category_id>/',
        views.category_articles,
        name='category_articles'
    ),

    path(
        'authors/',
        views.authors,
        name='authors'
    ),

    path(
        'authors/<int:author_id>/',
        views.author_articles,
        name='author_articles'
    ),

    path(
        'favorites/',
        views.favorites,
        name='favorites'
    ),

    path(
        'management/',
        views.management,
        name='management'
    ),

    path(
        'management/articles/<int:article_id>/toggle-publish/',
        views.toggle_article_publish,
        name='toggle_article_publish'
    ),

    path(
        'management/admins/',
        views.admin_management,
        name='admin_management'
    ),

    path(
        'management/admins/<int:user_id>/add/',
        views.make_admin,
        name='make_admin'
    ),

    path(
        'management/admins/<int:user_id>/remove/',
        views.remove_admin,
        name='remove_admin'
    ),




]