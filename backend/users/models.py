from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models

from .validators import validator_username


class User(AbstractUser):

    email = models.EmailField(
        verbose_name="email address",
        max_length=254, unique=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
