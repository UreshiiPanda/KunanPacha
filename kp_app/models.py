from django.db import models

# Create your models here.

class Test(models.Model):
    info = models.CharField(max_length=200)
    ready = models.BooleanField(default=False)



class Art1PageSettings(models.Model):
    font = models.CharField(max_length=100)
    font_color = models.CharField(max_length=7)  # Assuming HEX color
    edu_email = models.EmailField()



class UserCredential(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
