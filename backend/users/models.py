from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models

from .validators import validator_username


class User(AbstractUser):

    bio = models.TextField("Биография", null=False, blank=True)
    username = models.CharField(
        unique=True,
        max_length=150,
        validators=[
            ASCIIUsernameValidator(),
            validator_username,
        ],
    )
    first_name = models.CharField(
        max_length=150,
    )
    last_name = models.CharField(
        max_length=150,
    )
    password = models.CharField(
        max_length=150,
    )
    email = models.EmailField(
        verbose_name="email address",
        max_length=254, unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["username", "email"],
                name="unique_user")
        ]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username