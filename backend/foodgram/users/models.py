from django.contrib.auth.models import AbstractUser
from django.db import models

ROLES = (
    ('user', 'user'),
    ('admin', 'admin')
)


class CustomUser(AbstractUser):
    """Модель пользователя."""
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Имя пользователя'
    )
    email = models.CharField(
        max_length=254,
        unique=True
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль'
    )

    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f'{self.username}'


class Follow(models.Model):
    """Модель подписчика."""
    user = models.ForeignKey(
        CustomUser,
        related_name='follower',
        verbose_name='Подписчик',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        CustomUser,
        related_name='following',
        verbose_name='Автор',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('-author',)
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_followings')]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
