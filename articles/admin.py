from django.contrib import admin

from .models import Article, Category, Dislike, Favorite, Like, Rating


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'category',
        'is_published',
        'created_at',
        'updated_at',
    )
    list_filter = ('is_published', 'category', 'created_at')
    search_fields = ('title', 'text', 'author__username')
    list_editable = ('is_published',)
    autocomplete_fields = ('author', 'category')
    date_hierarchy = 'created_at'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('article', 'user')
    search_fields = ('article__title', 'user__username')


@admin.register(Dislike)
class DislikeAdmin(admin.ModelAdmin):
    list_display = ('article', 'user')
    search_fields = ('article__title', 'user__username')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('article', 'user')
    search_fields = ('article__title', 'user__username')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'value')
    list_filter = ('value',)
    search_fields = ('article__title', 'user__username')
