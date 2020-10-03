#!/usr/bin/env python3
# Copyright of Lizzy Trickster (Lizzy Green)

from django.db import models
import uuid
from django.contrib.auth.models import User
# Create your models here.


class Birthday(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)

    display_name = models.TextField(max_length=32)
    birthday = models.TextField(max_length=4)

    @property
    def get_day(self):
        return self.birthday[:2]

    @property
    def get_month(self):
        return self.birthday[2:]
