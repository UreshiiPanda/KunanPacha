from django.db import models

# Create your models here.


class Art1PageSettings(models.Model):
    font = models.CharField(max_length=100)
    # this will come in as a tailwind color class (eg: red-500)
    font_color = models.CharField(max_length=100)
    edu_email = models.EmailField()
    font_style = models.CharField(max_length=100)


class ArtCategoryPageSettings(models.Model):
    font = models.CharField(max_length=100)
    # this will come in as a tailwind color class (eg: red-500)
    font_color = models.CharField(max_length=100)
    edu_email = models.EmailField()
    font_style = models.CharField(max_length=100)


class ArtCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image1_filename = models.CharField(max_length=255)

    def __str__(self):
        return self.name


def get_default_category():
    return ArtCategory.objects.get_or_create(name="All")[0].id


class Artwork(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(
        ArtCategory,
        on_delete=models.SET_DEFAULT,
        default=get_default_category,
        related_name="artworks",
    )
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


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
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


class HomePage2Settings(models.Model):
    homepage2_text = models.TextField()
    font = models.CharField(max_length=100)
    # this will come in as a tailwind color class (eg: red-500)
    font_color = models.CharField(max_length=100)
    font_style = models.CharField(max_length=100)


class HomePage3Settings(models.Model):
    homepage3_text = models.TextField()
    font = models.CharField(max_length=100)
    # this will come in as a tailwind color class (eg: red-500)
    font_color = models.CharField(max_length=100)
    font_style = models.CharField(max_length=100)


class HomePage4Settings(models.Model):
    homepage4_text = models.TextField()
    font = models.CharField(max_length=100)
    # this will come in as a tailwind color class (eg: red-500)
    font_color = models.CharField(max_length=100)
    font_style = models.CharField(max_length=100)


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
