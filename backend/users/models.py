from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя Foodgram."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(
        'email',
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
    )
    first_name = models.CharField(
        'first name',
        max_length=150,
    )
    last_name = models.CharField(
        'last name',
        max_length=150,
    )
    avatar = models.ImageField(
        'avatar',
        upload_to='users/avatars/',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Подписка пользователя на автора рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author_subscription',
            ),
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
