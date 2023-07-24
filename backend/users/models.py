from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

from foodgram.settings import LENGTH_254


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        db_index=True,
        max_length=LENGTH_254,
        verbose_name='email'
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_subscription',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_subscription',
        verbose_name='Автор'
    )

    class Meta:
        ordering = ('user', 'author')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_Subscription'
            ),
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'

    def clean(self) -> None:
        if self.author == self.user:
            raise ValidationError('Нельзя подписаться на самого себя')
        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
