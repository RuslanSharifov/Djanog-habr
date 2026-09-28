
from django.contrib import admin

from .models import (
    Category,
    Article,
    Like,
    Dislike,
    Favorite,
    Rating
)

admin.site.register(Category)
admin.site.register(Article)
admin.site.register(Like)
admin.site.register(Dislike)
admin.site.register(Favorite)
admin.site.register(Rating)












