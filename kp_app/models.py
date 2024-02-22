from django.db import models

# Create your models here.

class Test(models.Model):
    info = models.CharField(max_length=200)
    ready = models.BooleanField(default=False)
