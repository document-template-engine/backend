from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validator_password


class User(AbstractUser):
    bio = models.TextField("Биография", null=True, blank=True)
    email = models.EmailField(
        verbose_name="email address",
        max_length=254,
        unique=True,
        error_messages={
            "unique": "Данная почта уже используется",
        },
    )
    password = models.CharField(
        max_length=150,
        validators=[
            validator_password,
        ],
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
