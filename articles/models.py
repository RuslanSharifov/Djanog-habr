from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    image = models.ImageField(
        upload_to='articles/',
        blank=True,
        null=True
    )

    author = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='articles'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='articles'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Like(models.Model):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE
    )

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('user', 'article')


class Dislike(models.Model):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE
    )

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('user', 'article')


class Favorite(models.Model):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE
    )

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('user', 'article')


class Rating(models.Model):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE
    )

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE
    )

    value = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )

    class Meta:
        unique_together = ('user', 'article')
