from django.db import models

# Create your models here.

class Test(models.Model):
    info = models.CharField(max_length=200)
    ready = models.BooleanField(default=False)


class UserCredential(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
