from django.db import models

# Create your models here.


class Art1PageSettings(models.Model):
    font = models.CharField(max_length=100)
    # this will come in as a tailwind color class (eg: red-500)
    font_color = models.CharField(max_length=100)
    edu_email = models.EmailField()
    font_style = models.CharField(max_length=100)


class Artwork(models.Model):
    title = models.CharField(max_length=200)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    print_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    dimensions = models.CharField(max_length=255)
    image1_filename = models.CharField(max_length=255)
    image2_filename = models.CharField(max_length=255, blank=True, null=True)
    image3_filename = models.CharField(max_length=255, blank=True, null=True)
    image4_filename = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Art2PageSettings(models.Model):
    font = models.CharField(max_length=100)
    # this will come in as a tailwind color class (eg: red-500)
    font_color = models.CharField(max_length=100)
    edu_email = models.EmailField()
    font_style = models.CharField(max_length=100)


class HomePage1Settings(models.Model):
    title = models.CharField(max_length=100)
    font = models.CharField(max_length=100)
    # this will come in as a tailwind color class (eg: red-500)
    font_color = models.CharField(max_length=100)
    font_style = models.CharField(max_length=100)

    # background_image from bucket


class HomePage2Settings(models.Model):
    homepage2_text = models.TextField()
    font = models.CharField(max_length=100)
   # this will come in as a tailwind color class (eg: red-500)
    font_color = models.CharField(max_length=100)
    font_style = models.CharField(max_length=100)

    # homepage_2_image_1 from bucket


class HomePage3Settings(models.Model):
    homepage3_text = models.TextField()
    font = models.CharField(max_length=100)
    # this will come in as a tailwind color class (eg: red-500)
    font_color = models.CharField(max_length=100)
    font_style = models.CharField(max_length=100)

    # homepage_3_image_1 from bucket


class HomePage4Settings(models.Model):
    homepage4_text = models.TextField()
    font = models.CharField(max_length=100)
    # this will come in as a tailwind color class (eg: red-500)
    font_color = models.CharField(max_length=100)
    font_style = models.CharField(max_length=100)

    # homepage_4_image_1 from bucket

class MenuSettings(models.Model):
    font = models.CharField(max_length=100)
    # this will come in as a tailwind color class (eg: red-500)
    font_color = models.CharField(max_length=100)
    font_style = models.CharField(max_length=100)


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


class BlogPageSettings(models.Model):
    font = models.CharField(max_length=100)
    # this will come in as a tailwind color class (eg: red-500)
    font_color = models.CharField(max_length=100)
    font_style = models.CharField(max_length=100)
    blog_title = models.CharField(max_length=100)
    blog_text = models.TextField()
    edu_facebook = models.URLField()
    edu_instagram = models.URLField()


class UserCredential(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
