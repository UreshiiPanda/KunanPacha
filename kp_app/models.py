from django.db import models

# Create your models here.


class Art1PageSettings(models.Model):
    font = models.CharField(max_length=100)
    # this will come in as a tailwind color class (eg: red-500)
    font_color = models.CharField(max_length=100)
    edu_email = models.EmailField()


class Art2PageSettings(models.Model):
    font = models.CharField(max_length=100)
    # this will come in as a tailwind color class (eg: red-500)
    font_color = models.CharField(max_length=100)
    edu_email = models.EmailField()


class HomePage1Settings(models.Model):
    title = models.CharField(max_length=100)
    # background_image from bucket


class HomePage2Settings(models.Model):
    homepage2_text = models.TextField()
    # homepage_2_image_1 from bucket


class HomePage3Settings(models.Model):
    homepage3_text = models.TextField()
    # homepage_3_image_1 from bucket


class HomePage4Settings(models.Model):
    homepage4_text = models.TextField()
    # homepage_4_image_1 from bucket


class ContactPageSettings(models.Model):
    font = models.CharField(max_length=100)
    # this will come in as a tailwind color class (eg: red-500)
    font_color = models.CharField(max_length=100)
    font_style = models.CharField(max_length=100)
    edu_address = models.CharField(max_length=100)
    edu_phone = models.CharField(max_length=100)
    edu_email = models.EmailField()
    edu_facebook = models.URLField()
    edu_instagram = models.URLField()


class UserCredential(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
