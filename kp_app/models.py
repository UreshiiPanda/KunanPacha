from django.db import models

# Create your models here.

class Test(models.Model):
    info = models.CharField(max_length=200)
    ready = models.BooleanField(default=False)



class Art1PageSettings(models.Model):
    font = models.CharField(max_length=100)
    # this will come in as a tailwind color class (eg: red-500)
    font_color = models.CharField(max_length=100)
    edu_email = models.EmailField()



class UserCredential(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
