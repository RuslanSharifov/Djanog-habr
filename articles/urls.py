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
        'article/<int:article_id>/rate/',
        views.article_rate,
        name='article_rate'
    ),
    path(
        'article/<int:article_id>/favorite/',
        views.article_favorite,
        name='article_favorite'
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

    path('popular/', views.popular, name='popular'),
    path('categories/', views.categories, name='categories'),
    path(
        'categories/<int:category_id>/',
        views.category_articles,
        name='category_articles'
    ),
    path('authors/', views.authors, name='authors'),
    path(
        'authors/<int:author_id>/',
        views.author_articles,
        name='author_articles'
    ),
    path('favorites/', views.favorites, name='favorites'),

    path(
        'management/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),
    path(
        'management/users/',
        views.admin_users,
        name='admin_users'
    ),
    path(
        'management/articles/<int:article_id>/approve/',
        views.approve_article,
        name='approve_article'
    ),
    path(
        'management/articles/<int:article_id>/reject/',
        views.reject_article,
        name='reject_article'
    ),
    path(
        'management/users/<int:user_id>/toggle-block/',
        views.toggle_user_block,
        name='toggle_user_block'
    ),
    path(
        'management/users/<int:user_id>/make-admin/',
        views.assign_admin,
        name='assign_admin'
    ),
    path(
        'management/users/<int:user_id>/remove-admin/',
        views.remove_admin,
        name='remove_admin'
    ),
]
