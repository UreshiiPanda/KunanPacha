from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from .models import *

# Register your models here.


class BlogPostAdmin(SummernoteModelAdmin):
    summernote_fields = ("description",)


admin.site.register(BlogPost, BlogPostAdmin)


admin.site.register(UserCredential)
admin.site.register(ArtCategoryPageSettings)
admin.site.register(Art1PageSettings)
admin.site.register(Art2PageSettings)
admin.site.register(HomePage1Settings)
admin.site.register(HomePage2Settings)
admin.site.register(HomePage3Settings)
admin.site.register(HomePage4Settings)
admin.site.register(ContactPageSettings)
admin.site.register(BlogPageSettings)
admin.site.register(MenuSettings)
admin.site.register(Artwork)
admin.site.register(ArtCategory)
