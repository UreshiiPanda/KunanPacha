import json
import os
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password, make_password
from django.core.files.storage import default_storage
from django.core.mail import BadHeaderError, send_mail
from django.core.paginator import EmptyPage, Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from dotenv import load_dotenv
from google.cloud import storage

from .forms import BlogPostForm, LoginForm, RegistrationForm
from .models import (Art1PageSettings, Art2PageSettings, ArtCategory,
                     ArtCategoryPageSettings, Artwork, BlogPageSettings,
                     BlogPost, ContactPageSettings, HomePage1Settings,
                     HomePage2Settings, HomePage3Settings, HomePage4Settings,
                     MenuSettings, UserCredential)

load_dotenv()



def art_categories(request):                                                                                              
    # Get all categories and order them by name
    categories = ArtCategory.objects.all().order_by('name')

    art_category_page_settings = ArtCategoryPageSettings.objects.first()
    if not art_category_page_settings:
        art_category_page_settings = ArtCategoryPageSettings.objects.create(
            font='sans-serif',
            font_color='black',
            font_style='normal',
        )


    menu_settings = MenuSettings.objects.first()
    if not menu_settings:
        menu_settings = MenuSettings.objects.create(
            font='sans-serif',
            font_color='black',
            font_style='normal',
        )
 

    # Prepare category data
    category_data = []
    for category in categories:
        if os.getenv("KP_PROD") == "false":
            # Local environment
            image_base_url = os.path.join(settings.STATIC_URL, 'kp_app/images/')
            image_urls = [
                os.path.join(image_base_url, category.image1_filename),
            ]
        else:
            # Production environment (GCP)
            image_base_url = f"{settings.STATIC_URL}kp_app/images/"
            image_urls = [
                f'{image_base_url}{category.image1_filename}',
            ]

        category_data.append({
            'id': category.id,
            'name': category.name,
            'image1': image_urls[0],
        })


    if os.getenv("KP_PROD") == "true":
        # Production environment (GCP)
        page_settings = {
            "font": art_category_page_settings.font,
            "font_color": art_category_page_settings.font_color,
            "font_style": art_category_page_settings.font_style,

            "menu_font": menu_settings.font,
            "menu_font_color": menu_settings.font_color,
            "menu_font_style": menu_settings.font_style,

        }
    else:
        # Local development environment
        page_settings = {
            "font": art_category_page_settings.font,
            "font_color": art_category_page_settings.font_color,
            "font_style": art_category_page_settings.font_style,

            "menu_font": menu_settings.font,
            "menu_font_color": menu_settings.font_color,
            "menu_font_style": menu_settings.font_style,
        }



    if request.headers.get('HX-Request') == 'true':
        print("art category page came from HTMX")
        return render(request, "art_categories_content.html", {"categories": category_data, "page_settings": page_settings})
    else:
        print("art category page did NOT come from HTMX")
        return render(request, "art_categories.html", {"categories": category_data, "page_settings": page_settings})




def add_art_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        images = [request.FILES.get(f'image{i}') for i in range(1, 2)]
    
        categories = ArtCategory.objects.all().order_by('name')

        # if new category name already exists
        if name in [category.name for category in categories] or name.lower() in [category.name.lower() for category in categories]:
            response = HttpResponse(status=400, content="Add Art Category form was given duplicate name")
            response['HX-Trigger'] = 'addArtDuplicateCategoryFailure'
            return response


        if not request.FILES.get('image1'):
            # if the user didn't input the first image (required)
            response = HttpResponse(status=400, content="Add Art Category form is missing image")
            response['HX-Trigger'] = 'addArtCategoryFailure'
            return response

        # make sure there is an image
        if name and images[0]:
            # Generate unique filenames for each image
            filenames = []
            # this still iterates from 0, but it makes the image naming convention start at 1
            for i, image in enumerate(images, start=1):
                if image:
                    ext = os.path.splitext(image.name)[1]
                    filename = f"{name.replace(' ', '_')}_{i}_{timezone.now().timestamp()}{ext}"
                    filenames.append(filename)

                    # Save image
                    if os.getenv("KP_PROD") == "false":

                        # Local storage
                        path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', filename)
                        print(f"local path add_art_category is adding to: {path}")
                        with open(path, 'wb+') as destination:
                            for chunk in image.chunks():
                                destination.write(chunk)
                    else:
                        # GCP Cloud Storage
                        client = storage.Client()
                        bucket = client.bucket(settings.GS_BUCKET_NAME)
                        blob = bucket.blob(f'kp_app/images/{filename}')
                        blob.upload_from_file(image)

            # Create Art_Category object
            # the create() func also performs .save() so we don't need to do artwork.save() after this
            art_category = ArtCategory.objects.create(
                name=name,
                image1_filename=filename,
            )

            return HttpResponseRedirect(reverse('art_categories'))
        else:
            print('from Add Art Category modal, All required fields must be filled and at least one image uploaded')
            return HttpResponse('from Add Art Category modal, All required fields must be filled and at least one image uploaded', status=400)

    return HttpResponse('from Add Art Category modal, add art category call was not a POST', status=400)




#@require_http_methods(["PUT"])
# the PUT was not detecting the FILES for some reason, but the POST works
def edit_art_category(request, art_category_id):
    art_category = get_object_or_404(ArtCategory, id=art_category_id)
    categories = ArtCategory.objects.all().order_by('name')


    if request.FILES.get('image1'):
        print(f'this is image1: {request.FILES.get("image1")}')

    if not request.FILES.get('image1'):
        # if the user didn't input the first image (required)
        response = HttpResponse(status=400, content="Edit Art Category form is missing image")
        response['HX-Trigger'] = 'editArtCategoryFailure'
        return response

    # if new category name already exists
    if art_category.name != request.POST.get('name') and (
            request.POST.get('name') in [category.name for category in categories] or
            request.POST.get('name') in [category.name.lower() for category in categories]):
        response = HttpResponse(status=400, content="Edit Art Category form was given duplicate name")
        response['HX-Trigger'] = 'addArtDuplicateCategoryFailure'
        return response


    if art_category.name != "All" and (request.POST.get('name') == 'all' or request.POST.get('name') == 'All'):
        response = HttpResponse(status=400, content="Edit Art Category form was given All name")
        response['HX-Trigger'] = 'addArtDuplicateCategoryFailure'
        return response


    # Update the fields
    # or leave them the same if the user didn't supply a new value
    art_category.name = request.POST.get('name', art_category.name)


    # Handle image updates
    for i in range(1, 2):
        image_field = f'image{i}'
        if image_field in request.FILES:
            image = request.FILES[image_field]
            ext = os.path.splitext(image.name)[1]
            filename = f"{art_category.name.replace(' ', '_')}_{i}_{timezone.now().timestamp()}{ext}"
            print(f"filename of image {i} being updated: {filename} for artwork {art_category.name}")
            
            # Save the new image
            if os.getenv("KP_PROD") == "false":
                # Local storage
                path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', filename)
                with open(path, 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)
            else:
                # GCP Cloud Storage
                client = storage.Client()
                bucket = client.bucket(settings.GS_BUCKET_NAME)
                blob = bucket.blob(f'kp_app/images/{filename}')
                blob.upload_from_file(image)

            # Delete the old image if it exists
            old_filename = getattr(art_category, f'image{i}_filename')
            if old_filename:
                if os.getenv("KP_PROD") == "false":
                    # Local Storage
                    old_path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', old_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                else:
                    # GCP Cloud Storage
                    bucket = client.bucket(settings.GS_BUCKET_NAME)
                    blob = bucket.blob(f'kp_app/images/{old_filename}')
                    if blob.exists():
                        blob.delete()

            # Update the filename in the model
            setattr(art_category, f'image{i}_filename', filename)
        else:
            # if the image is not in the request.FILES, then it needs to be deleted from the DB since
            # we are now refreshing the Edit Art form every time it is opened
            # Delete the old image if it exists
            setattr(art_category, f'image{i}_filename', None)
            


    # check if the user deleted any of the files via the removed input field that was
    # made to cirumvent Alpine issues
    # NOTE that image1 is not allowed to be removed by the user in the UI because an Artwork must
    # have at least 1 image
    # also check that the user didn't re-add a new image after clicking the trash bin icon for deletion
    for i in range(1, 2):
        if request.POST.get(f'removed{i}') == "true" and f'image{i}' not in request.FILES:
            print(f'removing image {i} from artwork {art_category.name}')
            setattr(art_category, f'image{i}_filename', None)
        
    art_category.save()
    return HttpResponseRedirect(reverse('art_categories'))



@require_http_methods(["DELETE"])
def delete_art_category(request, art_category_id):
    art_category = get_object_or_404(ArtCategory, id=art_category_id)

    if art_category.name == "All":
        response = HttpResponse(status=400, content="Cannot delete All art category")
        response['HX-Trigger'] = 'deleteArtCategoryFailure'
        return response
    
    # Delete images from GCP bucket if in production
    if os.getenv("KP_PROD") == "true":
        client = storage.Client()
        bucket = client.bucket(settings.GS_BUCKET_NAME)
        
        image_fields = [art_category.image1_filename]
        
        for image_filename in image_fields:
            if image_filename:
                blob = bucket.blob(f'kp_app/images/{image_filename}')
                if blob.exists():
                    blob.delete()
                    print(f"Deleted {image_filename} from GCP bucket")
    else:
        # Delete images from local storage if in development
        image_fields = [art_category.image1_filename]
 
        for image_filename in image_fields:
            if image_filename:
                image_path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', image_filename)
                if os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"Deleted {image_filename} from local storage")

    # Delete the artwork from the Postgres database
    art_category.delete()
    return HttpResponseRedirect(reverse('art_categories'))





def home(request):
    home_page_1_settings = HomePage1Settings.objects.first()
    home_page_2_settings = HomePage2Settings.objects.first()
    home_page_3_settings = HomePage3Settings.objects.first()
    home_page_4_settings = HomePage4Settings.objects.first()
    contact_page_settings = ContactPageSettings.objects.first()
    menu_settings = MenuSettings.objects.first()

    if not home_page_1_settings:
        home_page_1_settings = HomePage1Settings.objects.create(
            title='Title Here',
            font='sans-serif',
            font_color='black',
            font_style='normal',
        )
    if not home_page_2_settings:
        home_page_2_settings = HomePage2Settings.objects.create(
            homepage2_text='Text for home page 2 here',
            font='sans-serif',
            font_color='black',
            font_style='normal',
        )
    if not home_page_3_settings:
        home_page_3_settings = HomePage3Settings.objects.create(
            homepage3_text='Text for home page 3 here',
            font='sans-serif',
            font_color='black',
            font_style='normal',
        )
    if not home_page_4_settings:
        home_page_4_settings = HomePage4Settings.objects.create(
            homepage4_text='Text for home page 4 here',
            font='sans-serif',
            font_color='black',
            font_style='normal',
        )
    if not menu_settings:
        menu_settings = MenuSettings.objects.create(
            font='sans-serif',
            font_color='black',
            font_style='normal',
        )
    if not contact_page_settings:
        contact_page_settings = ContactPageSettings.objects.create(
            edu_address="Vilcabamba, Ecuador",
            edu_phone="+61 123-456-789",
            edu_email="edu@gmail.com",
            edu_facebook="www.facebook.com",
            edu_instagram="www.instagram.com",
            font="sans-serif",
            font_color="black",
            font_style="normal",
        )

    if os.getenv("KP_PROD") == "true":
        print("in home view in views.py, in PROD env, getting images from GCP")
        page_settings = {
            "title": home_page_1_settings.title,
            "background_image": f"{settings.STATIC_URL}kp_app/images/bg1.jpg",
            "homepage1_font": home_page_1_settings.font,
            "homepage1_font_color": home_page_1_settings.font_color,
            "homepage1_font_style": home_page_1_settings.font_style,

            "homepage2_text": home_page_2_settings.homepage2_text,
            "homepage_2_image_1": f"{settings.STATIC_URL}kp_app/images/art1.jpg",
            "homepage2_font": home_page_2_settings.font,
            "homepage2_font_color": home_page_2_settings.font_color,
            "homepage2_font_style": home_page_2_settings.font_style,

            "homepage3_text": home_page_3_settings.homepage3_text,
            "homepage3_font": home_page_3_settings.font,
            "homepage3_font_color": home_page_3_settings.font_color,
            "homepage3_font_style": home_page_3_settings.font_style,

            "homepage4_text": home_page_4_settings.homepage4_text,
            "homepage_4_image_1": f"{settings.STATIC_URL}kp_app/images/art3.jpg",
            "homepage4_font": home_page_4_settings.font,
            "homepage4_font_color": home_page_4_settings.font_color,
            "homepage4_font_style": home_page_4_settings.font_style,
 
            "menu_font": menu_settings.font,
            "menu_font_color": menu_settings.font_color,
            "menu_font_style": menu_settings.font_style,

            "contact_address": contact_page_settings.edu_address,
            "contact_phone": contact_page_settings.edu_phone,
            "contact_email": contact_page_settings.edu_email,
            "contact_facebook": contact_page_settings.edu_facebook,
            "contact_instagram": contact_page_settings.edu_instagram,
            "contact_font": contact_page_settings.font,
            "contact_font_color": contact_page_settings.font_color,
            "contact_font_style": contact_page_settings.font_style,
            "contact_image": f"{settings.STATIC_URL}kp_app/images/art4.jpg",
        }
    else:
        print("in home view in views.py, in DEV env, getting images from local files")
        page_settings = {
            "title": home_page_1_settings.title,
            "background_image": os.path.join("static/kp_app/images/bg1.jpg"),
            "homepage1_font": home_page_1_settings.font,
            "homepage1_font_color": home_page_1_settings.font_color,
            "homepage1_font_style": home_page_1_settings.font_style,

            "homepage2_text": home_page_2_settings.homepage2_text,
            "homepage_2_image_1": os.path.join("static/kp_app/images/art1.jpg"),
            "homepage2_font": home_page_2_settings.font,
            "homepage2_font_color": home_page_2_settings.font_color,
            "homepage2_font_style": home_page_2_settings.font_style,

            "homepage3_text": home_page_3_settings.homepage3_text,
            "homepage3_font": home_page_3_settings.font,
            "homepage3_font_color": home_page_3_settings.font_color,
            "homepage3_font_style": home_page_3_settings.font_style,

            "homepage4_text": home_page_4_settings.homepage4_text,
            "homepage_4_image_1": os.path.join("static/kp_app/images/art3.jpg"),
            "homepage4_font": home_page_4_settings.font,
            "homepage4_font_color": home_page_4_settings.font_color,
            "homepage4_font_style": home_page_4_settings.font_style,
 
            "menu_font": menu_settings.font,
            "menu_font_color": menu_settings.font_color,
            "menu_font_style": menu_settings.font_style,

            "contact_address": contact_page_settings.edu_address,
            "contact_phone": contact_page_settings.edu_phone,
            "contact_email": contact_page_settings.edu_email,
            "contact_facebook": contact_page_settings.edu_facebook,
            "contact_instagram": contact_page_settings.edu_instagram,
            "contact_font": contact_page_settings.font,
            "contact_font_color": contact_page_settings.font_color,
            "contact_font_style": contact_page_settings.font_style,
            "contact_image": os.path.join("static/kp_app/images/art4.jpg"),
        }

    print(f"current home page settings coming into the home view: {page_settings}")

    if request.headers.get('HX-Request') == 'true':
        print("home page came from HTMX")
        return render(request, "home_content.html", {"page_settings": page_settings})
    else:
        print("home page did NOT come from HTMX")
        return render(request, "home.html", {"page_settings": page_settings})



def contact(request):
    contact_page_settings = ContactPageSettings.objects.first()
    menu_settings = MenuSettings.objects.first()

    if not contact_page_settings:
        contact_page_settings = ContactPageSettings.objects.create(
            edu_address="Vilcabamba, Ecuador",
            edu_phone="+61 123-456-789",
            edu_email="edu@gmail.com",
            edu_facebook="www.facebook.com",
            edu_instagram="www.instagram.com",
            font="sans-serif",
            font_color="black",
            font_style="normal",
        )
    if not menu_settings:
        menu_settings = MenuSettings.objects.create(
            font='sans-serif',
            font_color='black',
            font_style='normal',
        )


    if os.getenv("KP_PROD") == "true":
        # Production environment (GCP)
        page_settings = {
            "contact_address": contact_page_settings.edu_address,
            "contact_phone": contact_page_settings.edu_phone,
            "contact_email": contact_page_settings.edu_email,
            "contact_facebook": contact_page_settings.edu_facebook,
            "contact_instagram": contact_page_settings.edu_instagram,
            "contact_font": contact_page_settings.font,
            "contact_font_color": contact_page_settings.font_color,
            "contact_font_style": contact_page_settings.font_style,
            "contact_image": f"{settings.STATIC_URL}kp_app/images/art4.jpg",

            "menu_font": menu_settings.font,
            "menu_font_color": menu_settings.font_color,
            "menu_font_style": menu_settings.font_style,

        }
    else:
        # Local development environment
        page_settings = {
            "contact_address": contact_page_settings.edu_address,
            "contact_phone": contact_page_settings.edu_phone,
            "contact_email": contact_page_settings.edu_email,
            "contact_facebook": contact_page_settings.edu_facebook,
            "contact_instagram": contact_page_settings.edu_instagram,
            "contact_font": contact_page_settings.font,
            "contact_font_color": contact_page_settings.font_color,
            "contact_font_style": contact_page_settings.font_style,
            "contact_image": os.path.join(settings.STATIC_URL, 'kp_app/images/art4.jpg'),

            "menu_font": menu_settings.font,
            "menu_font_color": menu_settings.font_color,
            "menu_font_style": menu_settings.font_style,

        }
    if request.headers.get('HX-Request') == 'true':
        print("contact page came from HTMX")
        return render(request, "contact_content.html", {"page_settings": page_settings})
    else:
        print("contact page did NOT come from HTMX")
        return render(request, "contact.html", {"page_settings": page_settings})



def blog(request, page="1"):
    blog_page_settings = BlogPageSettings.objects.first()
    menu_settings = MenuSettings.objects.first()

    if not blog_page_settings:
        blog_page_settings = BlogPageSettings.objects.create(
            blog_title="blog title here",
            blog_text="blog text here",
            edu_facebook="facebook here",
            edu_instagram="instagram here",
            font="sans-serif",
            font_color="black",
            font_style="normal",
        )
    if not menu_settings:
        menu_settings = MenuSettings.objects.create(
            font='sans-serif',
            font_color='black',
            font_style='normal',
        )

    if os.getenv("KP_PROD") == "true":
        # Production environment (GCP)
        page_settings = {
            "blog_title": blog_page_settings.blog_title,
            "blog_text": blog_page_settings.blog_text,
            "blog_facebook": blog_page_settings.edu_facebook,
            "blog_instagram": blog_page_settings.edu_instagram,
            "blog_font": blog_page_settings.font,
            "blog_font_color": blog_page_settings.font_color,
            "blog_font_style": blog_page_settings.font_style,
            "blog_bg_image": f"{settings.STATIC_URL}kp_app/images/blog_bg.jpg",
            "blog_logo_image": f"{settings.STATIC_URL}kp_app/images/blog_logo.jpg",

            "menu_font": menu_settings.font,
            "menu_font_color": menu_settings.font_color,
            "menu_font_style": menu_settings.font_style,

        }
    else:
        # Local development environment
        page_settings = {
            "blog_title": blog_page_settings.blog_title,
            "blog_text": blog_page_settings.blog_text,
            "blog_facebook": blog_page_settings.edu_facebook,
            "blog_instagram": blog_page_settings.edu_instagram,
            "blog_font": blog_page_settings.font,
            "blog_font_color": blog_page_settings.font_color,
            "blog_font_style": blog_page_settings.font_style,
            "blog_bg_image": os.path.join(settings.STATIC_URL, 'kp_app/images/blog_bg.jpg'),
            "blog_logo_image": os.path.join(settings.STATIC_URL, 'kp_app/images/blog_logo.jpg'),

            "menu_font": menu_settings.font,
            "menu_font_color": menu_settings.font_color,
            "menu_font_style": menu_settings.font_style,

        }


    # Fetch blog posts from the database
    blog_posts = BlogPost.objects.all().order_by('-created_at')


    # Use Django's paginator with 10 items per page for blog_post pages
    paginator = Paginator(blog_posts, 10)
    
    # Get the number of pages from the paginator
    num_pages = paginator.num_pages

    try:
        # Get the specified page
        blog_posts = paginator.page(page)
    except EmptyPage:
        # If the page is out of range, deliver last page of results
        blog_posts = paginator.page(paginator.num_pages)

    # Prepare blog post data
    all_blog_posts = []
    for post in blog_posts:
        if os.getenv("KP_PROD") == "false":
            # Local environment
            image_base_url = os.path.join(settings.STATIC_URL, 'kp_app/images/')
            image_urls = [
                os.path.join(image_base_url, post.image1_filename),
                os.path.join(image_base_url, post.image2_filename) if post.image2_filename else None,
                os.path.join(image_base_url, post.image3_filename) if post.image3_filename else None,
                os.path.join(image_base_url, post.image4_filename) if post.image4_filename else None,
            ]
        else:
            # Production environment (GCP)
            image_base_url = f"{settings.STATIC_URL}kp_app/images/"
            image_urls = [
                f'{image_base_url}{post.image1_filename}',
                f'{image_base_url}{post.image2_filename}' if post.image2_filename else None,
                f'{image_base_url}{post.image3_filename}' if post.image3_filename else None,
                f'{image_base_url}{post.image4_filename}' if post.image4_filename else None,
            ]


        # Filter out None values from image_urls
        filtered_images = [img for img in image_urls if img is not None]
        

        # the template uses both an array of the images and the individual images separately
        # as this was easier to do with the existing Alpine, so both will be included in the
        # context objects
        post_data = {
            'id': post.id,
            'title': post.title,
            'description': post.description,
            'images': filtered_images,  # Keep the filtered images array
            'date': post.created_at,
        }

        # Add individual image variables
        for i, image_url in enumerate(filtered_images, start=1):
            post_data[f'image{i}'] = image_url

        all_blog_posts.append(post_data)



    if request.headers.get('HX-Request') == 'true':
        print("blog page came from HTMX")
        # 2 separate forms were necessary to get around a weird Django error
        form_add = BlogPostForm(prefix='add')
        form_edit = BlogPostForm(prefix='edit')
        return render(request, "blog.html", {
            "page_settings": page_settings, 
            "blog_posts": all_blog_posts, 
            "form_add":form_add, 
            "form_edit":form_edit,
            "num_pages": num_pages,
            "page": page,
            })
    else:
        print("blog page did NOT come from HTMX")
        # 2 separate forms were necessary to get around a weird Django error
        form_add = BlogPostForm(prefix='add')
        form_edit = BlogPostForm(prefix='edit')
        return render(request, "blog.html", {
            "page_settings": page_settings, 
            "blog_posts": all_blog_posts, 
            "form_add":form_add, 
            "form_edit":form_edit,
            "num_pages": num_pages,
            "page": page,
            })


def blog2(request, post_id):
    # note that Django automatically adds an ID to every object in the models
    post = get_object_or_404(BlogPost, id=post_id)

    
    if os.getenv("KP_PROD") == "false":
        # Local environment
        image_base_url = os.path.join(settings.STATIC_URL, 'kp_app/images/')
        image_urls = [
            os.path.join(image_base_url, post.image1_filename),
            os.path.join(image_base_url, post.image2_filename) if post.image2_filename else None,
            os.path.join(image_base_url, post.image3_filename) if post.image3_filename else None,
            os.path.join(image_base_url, post.image4_filename) if post.image4_filename else None,
        ]
    else:
        # Production environment (GCP)
        image_base_url = f"{settings.STATIC_URL}kp_app/images/"
        image_urls = [
            f'{image_base_url}{post.image1_filename}',
            f'{image_base_url}{post.image2_filename}' if post.image2_filename else None,
            f'{image_base_url}{post.image3_filename}' if post.image3_filename else None,
            f'{image_base_url}{post.image4_filename}' if post.image4_filename else None,
        ]


    # Filter out None values from image_urls
    filtered_images = [img for img in image_urls if img is not None]
    
    # the template uses both an array of the images and the individual images separately
    # as this was easier to do with the existing Alpine, so both will be included in the
    # context objects
    post_data = {
        'id': post.id,
        'title': post.title,
        'description': post.description,
        'images': filtered_images,  # Keep the filtered images array
        'date': post.created_at,
    }

    # Add individual image variables
    for i, image_url in enumerate(filtered_images, start=1):
        post_data[f'image{i}'] = image_url


    if request.headers.get('HX-Request') == 'true':
        print("blog page 2 came from HTMX")
        # 2 separate forms were necessary to get around a weird Django error
        return render(request, "blog2_content.html", {"post": post_data})
    else:
        print("blog page 2 did NOT come from HTMX")

        # we only need to reload the page_settings if the user does not come from HTMX
        blog_page_settings = BlogPageSettings.objects.first()
        if not blog_page_settings:
            blog_page_settings = BlogPageSettings.objects.create(
                blog_title="blog title here",
                blog_text="blog text here",
                edu_facebook="facebook here",
                edu_instagram="instagram here",
                font="sans-serif",
                font_color="black",
                font_style="normal",
            )
            
        menu_settings = MenuSettings.objects.first()
        if not menu_settings:
            menu_settings = MenuSettings.objects.create(
                font='sans-serif',
                font_color='black',
                font_style='normal',
            )

        if os.getenv("KP_PROD") == "true":
            # Production environment (GCP)
            page_settings = {
                "blog_title": blog_page_settings.blog_title,
                "blog_text": blog_page_settings.blog_text,
                "blog_facebook": blog_page_settings.edu_facebook,
                "blog_instagram": blog_page_settings.edu_instagram,
                "blog_font": blog_page_settings.font,
                "blog_font_color": blog_page_settings.font_color,
                "blog_font_style": blog_page_settings.font_style,
                "blog_bg_image": f"{settings.STATIC_URL}kp_app/images/blog_bg.jpg",
                "blog_logo_image": f"{settings.STATIC_URL}kp_app/images/blog_logo.jpg",

                "menu_font": menu_settings.font,
                "menu_font_color": menu_settings.font_color,
                "menu_font_style": menu_settings.font_style,

            }
        else:
            # Local development environment
            page_settings = {
                "blog_title": blog_page_settings.blog_title,
                "blog_text": blog_page_settings.blog_text,
                "blog_facebook": blog_page_settings.edu_facebook,
                "blog_instagram": blog_page_settings.edu_instagram,
                "blog_font": blog_page_settings.font,
                "blog_font_color": blog_page_settings.font_color,
                "blog_font_style": blog_page_settings.font_style,
                "blog_bg_image": os.path.join(settings.STATIC_URL, 'kp_app/images/blog_bg.jpg'),
                "blog_logo_image": os.path.join(settings.STATIC_URL, 'kp_app/images/blog_logo.jpg'),

                "menu_font": menu_settings.font,
                "menu_font_color": menu_settings.font_color,
                "menu_font_style": menu_settings.font_style,

            }

        # 2 separate forms were necessary to get around a weird Django error
        return render(request, "blog2.html", {"post": post_data, "page_settings": page_settings})




def blog_page_edit(request):
    # Get the existing contact page settings
    blog_page = BlogPageSettings.objects.first()
    
    # If no settings exist, create a new one with default values
    if not blog_page:
        blog_page = BlogPageSettings.objects.create(
            blog_title="blog title here",
            blog_text="blog text here",
            edu_facebook="facebook here",
            edu_instagram="instagram here",
            font="sans-serif",
            font_color="black",
            font_style="normal",
        )

    # if the user changed the social media links, then the contact page will also need those updates
    # Get the existing contact page settings
    contact_page = ContactPageSettings.objects.first()
    
    # If no settings exist, create a new one with default values
    if not contact_page:
        contact_page = ContactPageSettings.objects.create(
            edu_address="address here",
            edu_phone="phone here",
            edu_email="email here",
            edu_facebook="facebook here",
            edu_instagram="instagram here",
            font="sans-serif",
            font_color="black",
            font_style="normal",
        )



    # Update fields only if new values are provided, otherwise just use the prev value
    blog_page.blog_title = request.POST.get('blog_title') or blog_page.blog_title
    blog_page.blog_text = request.POST.get('blog_text') or blog_page.blog_text
    blog_page.edu_facebook = request.POST.get('contact_facebook') or blog_page.edu_facebook
    blog_page.edu_instagram = request.POST.get('contact_instagram') or blog_page.edu_instagram
    blog_page.font = request.POST.get('blog_font') or blog_page.font
    blog_page.font_color = request.POST.get('blog_font_color') or blog_page.font_color
    blog_page.font_style = request.POST.get('blog_font_style') or blog_page.font_style

    blog_bg_image = request.FILES.get('blog_bg_image')
    blog_logo_image = request.FILES.get('blog_logo_image')

    # if the user changed the social media links, then the contact page will also need those updates
    contact_page.edu_facebook = request.POST.get('contact_facebook') or contact_page.edu_facebook
    contact_page.edu_instagram = request.POST.get('contact_instagram') or contact_page.edu_instagram

 
    print(f"Updating Blog Page settings: {
        blog_page.blog_title, 
        blog_page.blog_text, 
        blog_page.edu_facebook,
        blog_page.edu_instagram,
        blog_page.font,
        blog_page.font_color,
        blog_page.font_style,
    }, Blog BG image: {'Provided' if blog_bg_image else 'Not provided'}, Blog Logo image: {'Provided' if blog_logo_image else 'Not provided'}")
    
    try:
        if blog_bg_image:
            if os.getenv("KP_PROD") == "true":
                # GCP Production Environment
                client = storage.Client()
                bucket = client.get_bucket(settings.GS_BUCKET_NAME)
                blob = bucket.blob('kp_app/images/blog_bg.jpg')
                blob.upload_from_string(
                    blog_bg_image.read(),
                    content_type=blog_bg_image.content_type
                )
                print(f"New contact image saved to GCS: {blob.public_url}")
            else:
                # Local Development Environment
                image_path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', 'blog_bg.jpg')
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                with open(image_path, 'wb+') as destination:
                    for chunk in blog_bg_image.chunks():
                        destination.write(chunk)
                print(f"New Blog image saved to {image_path}")

        if blog_logo_image:
            if os.getenv("KP_PROD") == "true":
                # GCP Production Environment
                client = storage.Client()
                bucket = client.get_bucket(settings.GS_BUCKET_NAME)
                blob = bucket.blob('kp_app/images/blog_logo.jpg')
                blob.upload_from_string(
                    blog_logo_image.read(),
                    content_type=blog_logo_image.content_type
                )
                print(f"New contact image saved to GCS: {blob.public_url}")
            else:
                # Local Development Environment
                image_path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', 'blog_logo.jpg')
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                with open(image_path, 'wb+') as destination:
                    for chunk in blog_logo_image.chunks():
                        destination.write(chunk)
                print(f"New Blog image saved to {image_path}")


        blog_page.save()

        # if the user changed the social media links, then the contact page will also need those updates
        contact_page.save()
        print("Blog Page settings updated with new user input and saved to the DB")
        
        return HttpResponseRedirect(reverse('blog'))
    
    except Exception as e:
        print(f"Error saving Blog Page settings: {e}")
        response = HttpResponse(status=400, content="Contact Blog Settings update failed")
        return response



def add_blog(request):
    if request.method == 'POST':
        title = request.POST.get('blog_title')
        #description = request.POST.get('blog_description')
        images = [request.FILES.get(f'image{i}') for i in range(1, 5)]

        form = BlogPostForm(request.POST, prefix='add')
        if form.is_valid():
            description = form.cleaned_data['description']
        else:
            print("Form errors:", form.errors)
            response = HttpResponse(status=400, content="Add Blog form had an invalid Summernote description form")
            response['HX-Trigger'] = 'BlogDescFailure'
            return response


        if not request.FILES.get('image1'):
            # if the user didn't input the first image (required)
            response = HttpResponse(status=400, content="Add Blog form is missing first image")
            response['HX-Trigger'] = 'addBlogFailure'
            return response

        # make sure there is at least 1 image, the rest are optional
        if title and images[0]:
            # Generate unique filenames for each image
            filenames = []
            # this still iterates from 0, but it makes the image naming convention start at 1
            for i, image in enumerate(images, start=1):
                if image:
                    ext = os.path.splitext(image.name)[1]
                    filename = f"{title.replace(' ', '_')}_{i}_{timezone.now().timestamp()}{ext}"
                    filenames.append(filename)

                    # Save image
                    if os.getenv("KP_PROD") == "false":

                        # Local storage
                        path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', filename)
                        print(f"local path add_blog is adding to: {path}")
                        with open(path, 'wb+') as destination:
                            for chunk in image.chunks():
                                destination.write(chunk)
                    else:
                        # GCP Cloud Storage
                        client = storage.Client()
                        bucket = client.bucket(settings.GS_BUCKET_NAME)
                        blob = bucket.blob(f'kp_app/images/{filename}')
                        blob.upload_from_file(image)

            # Create BlogPost object
            # the create() func also performs .save() so we don't need to do blog_post.save() after this
            blog_post = BlogPost.objects.create(
                title=title,
                description=description,
                # the blog_date field is auto-generated on the Model-level
                image1_filename=filenames[0],
                image2_filename=filenames[1] if len(filenames) > 1 else None,
                image3_filename=filenames[2] if len(filenames) > 2 else None,
                image4_filename=filenames[3] if len(filenames) > 3 else None
            )

            return HttpResponseRedirect(reverse('blog'))
        else:
            print('from Add Blog modal, All required fields must be filled and at least one image uploaded')
            return HttpResponse('from Add Blog modal, All required fields must be filled and at least one image uploaded', status=400)

    else:
        print("request for add_blog was not a POST")



#@require_http_methods(["PUT"])
# the PUT was not detecting the FILES for some reason, but the POST works
def edit_blog(request, blog_id):
    blog_post = get_object_or_404(BlogPost, id=blog_id)


    if request.FILES.get('image1'):
        print(f'this is image1: {request.FILES.get("image1")}')
    if request.FILES.get('image2'):
        print(f'this is image2: {request.FILES.get("image2")}')
    if request.FILES.get('image3'):
        print(f'this is image3: {request.FILES.get("image3")}')
    if request.FILES.get('image4'):
        print(f'this is image4: {request.FILES.get("image4")}')

    if not request.FILES.get('image1'):
        # if the user didn't input the first image (required)
        response = HttpResponse(status=400, content="Edit Blog form is missing first image")
        response['HX-Trigger'] = 'editBlogFailure'
        return response



    # Update the basic fields
    # or leave them the same if the user didn't supply a new value
    blog_post.title = request.POST.get('title', blog_post.title)
    #blog_post.description = request.POST.get('description', blog_post.description)

    form = BlogPostForm(request.POST, prefix='edit')
    print("PREV DESCRIPTION: ", blog_post.description)
    description = None
    if form.is_valid():
        description = form.cleaned_data['description']
    else:
        print("Form errors:", form.errors)
        response = HttpResponse(status=400, content="Add Blog form had an invalid Summernote description form")
        response['HX-Trigger'] = 'BlogDescFailure'
        return response
    blog_post.description = description if description else blog_post.description


    # Handle image updates
    for i in range(1, 5):
        image_field = f'image{i}'
        if image_field in request.FILES:
            image = request.FILES[image_field]
            ext = os.path.splitext(image.name)[1]
            filename = f"{blog_post.title.replace(' ', '_')}_{i}_{timezone.now().timestamp()}{ext}"
            print(f"filename of image {i} being updated: {filename} for artwork {blog_post.title}")
            
            # Save the new image
            if os.getenv("KP_PROD") == "false":
                # Local storage
                path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', filename)
                with open(path, 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)
            else:
                # GCP Cloud Storage
                client = storage.Client()
                bucket = client.bucket(settings.GS_BUCKET_NAME)
                blob = bucket.blob(f'kp_app/images/{filename}')
                blob.upload_from_file(image)

            # Delete the old image if it exists
            old_filename = getattr(blog_post, f'image{i}_filename')
            if old_filename:
                if os.getenv("KP_PROD") == "false":
                    # Local Storage
                    old_path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', old_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                else:
                    # GCP Cloud Storage
                    bucket = client.bucket(settings.GS_BUCKET_NAME)
                    blob = bucket.blob(f'kp_app/images/{old_filename}')
                    if blob.exists():
                        blob.delete()

            # Update the filename in the model
            setattr(blog_post, f'image{i}_filename', filename)
        else:
            # if the image is not in the request.FILES, then it needs to be deleted from the DB since
            # we are now refreshing the Edit Art form every time it is opened
            # Delete the old image if it exists
            setattr(blog_post, f'image{i}_filename', None)
            


    # check if the user deleted any of the files via the removed input field that was
    # made to cirumvent Alpine issues
    # NOTE that image1 is not allowed to be removed by the user in the UI because an Artwork must
    # have at least 1 image
    # also check that the user didn't re-add a new image after clicking the trash bin icon for deletion
    for i in range(1, 5):
        if request.POST.get(f'removed{i}') == "true" and f'image{i}' not in request.FILES:
            print(f'removing image {i} from blog post {blog_post.title}')
            setattr(blog_post, f'image{i}_filename', None)
        
    blog_post.save()
    return HttpResponseRedirect(reverse('blog'))



@require_http_methods(["DELETE"])
def delete_blog(request, blog_id):
    blog_post = get_object_or_404(BlogPost, id=blog_id)
    
    # Delete images from GCP bucket if in production
    if os.getenv("KP_PROD") == "true":
        client = storage.Client()
        bucket = client.bucket(settings.GS_BUCKET_NAME)
        
        image_fields = [blog_post.image1_filename, blog_post.image2_filename, 
                        blog_post.image3_filename, blog_post.image4_filename]
        
        for image_filename in image_fields:
            if image_filename:
                blob = bucket.blob(f'kp_app/images/{image_filename}')
                if blob.exists():
                    blob.delete()
                    print(f"Deleted {image_filename} from GCP bucket")
    else:
        # Delete images from local storage if in development
        image_fields = [blog_post.image1_filename, blog_post.image2_filename, 
                        blog_post.image3_filename, blog_post.image4_filename]
        
        for image_filename in image_fields:
            if image_filename:
                image_path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', image_filename)
                if os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"Deleted {image_filename} from local storage")

    # Delete the artwork from the Postgres database
    blog_post.delete()
    return HttpResponseRedirect(reverse('blog'))



def art1(request, category_id):
    # get artworks based on category
    if category_id:                                                                                                       
        artworks = Artwork.objects.filter(category_id=category_id).order_by('-created_at') 
    else:                                                                                                                 
        artworks = Artwork.objects.all().order_by('-created_at')


    art_page_settings = Art1PageSettings.objects.first()
    if not art_page_settings:
        art_page_settings = Art1PageSettings.objects.create(
            font='sans-serif',
            font_color='black',
            font_style='normal',
            edu_email='jojohoughton22@gmail.com'
        )


    menu_settings = MenuSettings.objects.first()
    if not menu_settings:
        menu_settings = MenuSettings.objects.create(
            font='sans-serif',
            font_color='black',
            font_style='normal',
        )

     

    # Prepare artwork data
    artwork_data = []
    for artwork in artworks:
        if os.getenv("KP_PROD") == "false":
            # Local environment
            image_base_url = os.path.join(settings.STATIC_URL, 'kp_app/images/')
            image_urls = [
                os.path.join(image_base_url, artwork.image1_filename),
                os.path.join(image_base_url, artwork.image2_filename) if artwork.image2_filename else None,
                os.path.join(image_base_url, artwork.image3_filename) if artwork.image3_filename else None,
                os.path.join(image_base_url, artwork.image4_filename) if artwork.image4_filename else None,
            ]
        else:
            # Production environment (GCP)
            image_base_url = f"{settings.STATIC_URL}kp_app/images/"
            image_urls = [
                f'{image_base_url}{artwork.image1_filename}',
                f'{image_base_url}{artwork.image2_filename}' if artwork.image2_filename else None,
                f'{image_base_url}{artwork.image3_filename}' if artwork.image3_filename else None,
                f'{image_base_url}{artwork.image4_filename}' if artwork.image4_filename else None,
            ]

        artwork_data.append({
            'id': artwork.id,
            'title': artwork.title,
            'art_category': artwork.category,
            'original_price': artwork.original_price,
            'print_price': artwork.print_price,
            'description': artwork.description,
            'dimensions': artwork.dimensions,
            'image1': image_urls[0],
            'image2': image_urls[1],
            'image3': image_urls[2],
            'image4': image_urls[3],
            'created_at': artwork.created_at,
            'updated_at': artwork.updated_at,
        })


    if os.getenv("KP_PROD") == "true":
        # Production environment (GCP)
        page_settings = {
            "font": art_page_settings.font,
            "font_color": art_page_settings.font_color,
            "font_style": art_page_settings.font_style,

            "menu_font": menu_settings.font,
            "menu_font_color": menu_settings.font_color,
            "menu_font_style": menu_settings.font_style,

        }
    else:
        # Local development environment
        page_settings = {
            "font": art_page_settings.font,
            "font_color": art_page_settings.font_color,
            "font_style": art_page_settings.font_style,

            "menu_font": menu_settings.font,
            "menu_font_color": menu_settings.font_color,
            "menu_font_style": menu_settings.font_style,
        }



    if request.headers.get('HX-Request') == 'true':
        print("art1 page came from HTMX")
        return render(request, "art1_content.html", {"artworks": artwork_data, "page_settings": page_settings})
    else:
        print("art1 page did NOT come from HTMX")
        return render(request, "art1.html", {"artworks": artwork_data, "page_settings": page_settings})




def add_art(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        category = request.POST.get('art_category')
        original_price = request.POST.get('original_price')
        print_price = request.POST.get('print_price')
        description = request.POST.get('description')
        dimensions = request.POST.get('dimensions')
        images = [request.FILES.get(f'image{i}') for i in range(1, 5)]

        # check for valid category
        # if category == "all": category = "All"
        categories = ArtCategory.objects.all()
        print(f"CURR CATEGORIES: {[category.name.lower() for category in categories]}")
        print(f"ADD ART CURR CATEGORIES: {category.lower()}")
        if category.lower() not in [category.name.lower() for category in categories]:
            response = HttpResponse(status=400, content="That Category does not exist")
            response['HX-Trigger'] = 'addArtInvalidCategoryFailure'
            return response
 

        try:
            Decimal(original_price)
            Decimal(print_price)
        except InvalidOperation:
            response = HttpResponse(status=400, content="The Prices were not valid numbers")
            response['HX-Trigger'] = 'priceFailure'
            return response


        if not request.FILES.get('image1'):
            # if the user didn't input the first image (required)
            response = HttpResponse(status=400, content="Add Art form is missing first image")
            response['HX-Trigger'] = 'addArtFailure'
            return response

        # make sure there is at least 1 image, the rest are optional
        if title and category and original_price and print_price and description and dimensions and images[0]:
            # Generate unique filenames for each image
            filenames = []
            # this still iterates from 0, but it makes the image naming convention start at 1
            for i, image in enumerate(images, start=1):
                if image:
                    ext = os.path.splitext(image.name)[1]
                    filename = f"{title.replace(' ', '_')}_{i}_{timezone.now().timestamp()}{ext}"
                    filenames.append(filename)

                    # Save image
                    if os.getenv("KP_PROD") == "false":

                        # Local storage
                        path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', filename)
                        print(f"local path add_art is adding to: {path}")
                        with open(path, 'wb+') as destination:
                            for chunk in image.chunks():
                                destination.write(chunk)
                    else:
                        # GCP Cloud Storage
                        client = storage.Client()
                        bucket = client.bucket(settings.GS_BUCKET_NAME)
                        blob = bucket.blob(f'kp_app/images/{filename}')
                        blob.upload_from_file(image)

            # Create Artwork object
            # the create() func also performs .save() so we don't need to do artwork.save() after this
            # and make sure to get the category id for the DB instead of the name
            category_obj = ArtCategory.objects.get(name=category)
            category_id = category_obj.id
            artwork = Artwork.objects.create(
                title=title,
                category=category_obj,
                original_price=original_price,
                print_price=print_price,
                description=description,
                dimensions=dimensions,
                image1_filename=filenames[0],
                image2_filename=filenames[1] if len(filenames) > 1 else None,
                image3_filename=filenames[2] if len(filenames) > 2 else None,
                image4_filename=filenames[3] if len(filenames) > 3 else None
            )

            return HttpResponseRedirect(reverse('art1', args=[category_id]))
        else:
            print('from Add Art modal, All required fields must be filled and at least one image uploaded')
            return HttpResponse('from Add Art modal, All required fields must be filled and at least one image uploaded', status=400)

    return HttpResponse('from Add Art modal, add art call was not a POST', status=400)





#@require_http_methods(["PUT"])
# the PUT was not detecting the FILES for some reason, but the POST works
def edit_artwork(request, artwork_id):
    artwork = get_object_or_404(Artwork, id=artwork_id)


    if request.FILES.get('image1'):
        print(f'this is image1: {request.FILES.get("image1")}')
    if request.FILES.get('image2'):
        print(f'this is image2: {request.FILES.get("image2")}')
    if request.FILES.get('image3'):
        print(f'this is image3: {request.FILES.get("image3")}')
    if request.FILES.get('image4'):
        print(f'this is image4: {request.FILES.get("image4")}')

    if not request.FILES.get('image1'):
        # if the user didn't input the first image (required)
        response = HttpResponse(status=400, content="Edit Art form is missing first image")
        response['HX-Trigger'] = 'editArtFailure'
        return response



    # Update the basic fields
    # or leave them the same if the user didn't supply a new value
    artwork.title = request.POST.get('title', artwork.title)
    new_category_name = request.POST.get('art_category', artwork.category.name)
    new_category = ArtCategory.objects.get(name=new_category_name)
    artwork.category = new_category
    artwork.original_price = request.POST.get('original_price', artwork.original_price)
    artwork.print_price = request.POST.get('print_price', artwork.print_price)
    artwork.description = request.POST.get('description', artwork.description)
    artwork.dimensions = request.POST.get('dimensions', artwork.dimensions)

    # check for valid category
    categories = ArtCategory.objects.all()
    if new_category_name.lower() not in [category.name.lower() for category in categories]:
        response = HttpResponse(status=400, content="That Category does not exist")
        # re-use the addArt trigger cuz it's the same
        response['HX-Trigger'] = 'addArtInvalidCategoryFailure'
        return response


    try:
        Decimal(artwork.original_price)
        Decimal(artwork.print_price)
    except InvalidOperation:
        response = HttpResponse(status=400, content="The Prices were not valid numbers")
        response['HX-Trigger'] = 'priceFailure'
        return response


    # Handle image updates
    for i in range(1, 5):
        image_field = f'image{i}'
        if image_field in request.FILES:
            image = request.FILES[image_field]
            ext = os.path.splitext(image.name)[1]
            filename = f"{artwork.title.replace(' ', '_')}_{i}_{timezone.now().timestamp()}{ext}"
            print(f"filename of image {i} being updated: {filename} for artwork {artwork.title}")
            
            # Save the new image
            if os.getenv("KP_PROD") == "false":
                # Local storage
                path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', filename)
                with open(path, 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)
            else:
                # GCP Cloud Storage
                client = storage.Client()
                bucket = client.bucket(settings.GS_BUCKET_NAME)
                blob = bucket.blob(f'kp_app/images/{filename}')
                blob.upload_from_file(image)

            # Delete the old image if it exists
            old_filename = getattr(artwork, f'image{i}_filename')
            if old_filename:
                if os.getenv("KP_PROD") == "false":
                    # Local Storage
                    old_path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', old_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                else:
                    # GCP Cloud Storage
                    bucket = client.bucket(settings.GS_BUCKET_NAME)
                    blob = bucket.blob(f'kp_app/images/{old_filename}')
                    if blob.exists():
                        blob.delete()

            # Update the filename in the model
            setattr(artwork, f'image{i}_filename', filename)
        else:
            # if the image is not in the request.FILES, then it needs to be deleted from the DB since
            # we are now refreshing the Edit Art form every time it is opened
            # Delete the old image if it exists
            setattr(artwork, f'image{i}_filename', None)
            


    # check if the user deleted any of the files via the removed input field that was
    # made to cirumvent Alpine issues
    # NOTE that image1 is not allowed to be removed by the user in the UI because an Artwork must
    # have at least 1 image
    # also check that the user didn't re-add a new image after clicking the trash bin icon for deletion
    for i in range(1, 5):
        if request.POST.get(f'removed{i}') == "true" and f'image{i}' not in request.FILES:
            print(f'removing image {i} from artwork {artwork.title}')
            setattr(artwork, f'image{i}_filename', None)
        
    artwork.save()
    return HttpResponseRedirect(reverse('art1', args=[artwork.category.id]))




@require_http_methods(["DELETE"])
def delete_artwork(request, artwork_id):
    artwork = get_object_or_404(Artwork, id=artwork_id)
    
    # Delete images from GCP bucket if in production
    if os.getenv("KP_PROD") == "true":
        client = storage.Client()
        bucket = client.bucket(settings.GS_BUCKET_NAME)
        
        image_fields = [artwork.image1_filename, artwork.image2_filename, 
                        artwork.image3_filename, artwork.image4_filename]
        
        for image_filename in image_fields:
            if image_filename:
                blob = bucket.blob(f'kp_app/images/{image_filename}')
                if blob.exists():
                    blob.delete()
                    print(f"Deleted {image_filename} from GCP bucket")
    else:
        # Delete images from local storage if in development
        image_fields = [artwork.image1_filename, artwork.image2_filename, 
                        artwork.image3_filename, artwork.image4_filename]
        
        for image_filename in image_fields:
            if image_filename:
                image_path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', image_filename)
                if os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"Deleted {image_filename} from local storage")

    
    category_id = artwork.category.id
    # Delete the artwork from the Postgres database
    artwork.delete()
    return HttpResponseRedirect(reverse('art1', args=[category_id]))




def art2(request, artwork_id):
    # note that Django automatically adds an ID to every object in the models
    artwork = get_object_or_404(Artwork, id=artwork_id)
    
    art_page_settings = Art2PageSettings.objects.first()
    if not art_page_settings:
        art_page_settings = Art2PageSettings.objects.create(
            font='sans-serif',
            font_color='black',
            font_style='normal',
            edu_email='meow@email.com'
        )

    menu_settings = MenuSettings.objects.first()
    if not menu_settings:
        menu_settings = MenuSettings.objects.create(
            font='sans-serif',
            font_color='black',
            font_style='normal',
        )


    # Determine the environment and set image URLs accordingly
    if os.getenv("KP_PROD") == "true":
        # GCP environment
        image_base_url = f"{settings.STATIC_URL}kp_app/images/"
    else:
        # Local environment
        image_base_url = os.path.join(settings.STATIC_URL, 'kp_app/images/')

    image_obj = {
        'title': artwork.title,
        'desc': artwork.description,
        'dimensions': artwork.dimensions,
        'print_price': artwork.print_price,
        'original_price': artwork.original_price,
        'image': image_base_url + artwork.image1_filename,
        'image2': image_base_url + artwork.image2_filename if artwork.image2_filename else None,
        'image3': image_base_url + artwork.image3_filename if artwork.image3_filename else None,
        'image4': image_base_url + artwork.image4_filename if artwork.image4_filename else None,
    }

    if os.getenv("KP_PROD") == "true":
        # Production environment (GCP)
        page_settings = {
            "font": art_page_settings.font,
            "font_color": art_page_settings.font_color,
            "font_style": art_page_settings.font_style,

            "menu_font": menu_settings.font,
            "menu_font_color": menu_settings.font_color,
            "menu_font_style": menu_settings.font_style,

        }
    else:
        # Local development environment
        page_settings = {
            "font": art_page_settings.font,
            "font_color": art_page_settings.font_color,
            "font_style": art_page_settings.font_style,

            "menu_font": menu_settings.font,
            "menu_font_color": menu_settings.font_color,
            "menu_font_style": menu_settings.font_style,
        }


    context = {
        "image_obj": image_obj,
        "page_settings": page_settings,
        "art_category_id": artwork.category.id
    }

    if request.headers.get('HX-Request') == 'true':
        return render(request, 'art2_content.html', context)
    else:
        return render(request, 'art2.html', context)




def send_email(request):
    if request.method == "POST":
        name = request.POST.get("name", "")
        message = request.POST.get("message", "")
        user_email = request.POST.get("email", "")
        from_email = settings.EMAIL_HOST_USER
        email_subject = 'New Message from KP website'
        email_body = f'\nName: {name}\n\nEmail: {user_email}\n\nMessage: {message}'
        if name and message and from_email:
            try:
                send_mail(email_subject, email_body, from_email, ["jojohoughton22@gmail.com"], fail_silently=False)
                print("Email successfully sent")
            except BadHeaderError:
                response = HttpResponse(status=500, content="Invalid header found when sending email")
                response['HX-Trigger'] = 'emailFailureHeaders'
                return response
            response = HttpResponse(status=200, content="Email successfully sent")
            response['HX-Trigger'] = 'emailSuccess'
            return response
        else:
            # In reality we'd use a form class
            # to get proper validation errors.
            response = HttpResponse(status=400, content="Please make sure all fields are entered and valid")
            response['HX-Trigger'] = 'emailFailureFields'
            return response



def login_admin(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # user auth was successful
                # return an HTMX success response
                # hash the password before saving it to the database
                hashed_password = make_password(password)
                UserCredential.objects.create(username=username, password=hashed_password)
                print(f"user login successful for user: {user}")
                # save the user credentials to the database
                UserCredential.objects.create(username=username, password=password)
                login(request, user)
                response = HttpResponse(status=200, content="Successful Admin Login")
                response['HX-Trigger'] = 'loginSuccess'
                #return response
                return render(request, "home.html")
            else:
                # user auth has failed
                # return an HTMX failure response
                print(f"user login failed for user: {user}")
                response = HttpResponse(status=400, content="Invalid Login Credentials")
                response['HX-Trigger'] = 'loginFailure'
                return response


    else:
        # request was a GET to get the login page
        form = LoginForm()
    return render(request, 'login.html', {'form': form})



def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})





def contact_edit(request):
    # Get the existing contact page settings
    contact_page = ContactPageSettings.objects.first()
    
    # If no settings exist, create a new one with default values
    if not contact_page:
        contact_page = ContactPageSettings.objects.create(
            edu_address="address here",
            edu_phone="phone here",
            edu_email="email here",
            edu_facebook="facebook here",
            edu_instagram="instagram here",
            font="sans-serif",
            font_color="black",
            font_style="normal",
        )


    # if the user changed the social media links, then the contact page will also need those updates
    # Get the existing contact page settings
    blog_page = BlogPageSettings.objects.first()
    
    # If no settings exist, create a new one with default values
    if not blog_page:
        blog_page = BlogPageSettings.objects.create(
            blog_title="blog title here",
            blog_text="blog text here",
            edu_facebook="facebook here",
            edu_instagram="instagram here",
            font="sans-serif",
            font_color="black",
            font_style="normal",
        )


    # Update fields only if new values are provided, otherwise just use the prev value
    contact_page.edu_address = request.POST.get('contact_address') or contact_page.edu_address
    contact_page.edu_phone = request.POST.get('contact_phone') or contact_page.edu_phone
    contact_page.edu_email = request.POST.get('contact_email') or contact_page.edu_email
    contact_page.edu_facebook = request.POST.get('contact_facebook') or contact_page.edu_facebook
    contact_page.edu_instagram = request.POST.get('contact_instagram') or contact_page.edu_instagram
    contact_page.font = request.POST.get('contact_font') or contact_page.font
    contact_page.font_color = request.POST.get('contact_font_color') or contact_page.font_color
    contact_page.font_style = request.POST.get('contact_font_style') or contact_page.font_style

    contact_image = request.FILES.get('contact_image')

    # if the user changed the social media links, then the contact page will also need those updates
    blog_page.edu_facebook = request.POST.get('contact_facebook') or blog_page.edu_facebook
    blog_page.edu_instagram = request.POST.get('contact_instagram') or blog_page.edu_instagram

    
    print(f"Updating Contact Page settings: {
        contact_page.edu_address, 
        contact_page.edu_phone, 
        contact_page.edu_email,
        contact_page.edu_facebook,
        contact_page.edu_instagram,
        contact_page.font,
        contact_page.font_color,
        contact_page.font_style,
    }, image: {'Provided' if contact_image else 'Not provided'}")
    
    try:
        if contact_image:
            if os.getenv("KP_PROD") == "true":
                # GCP Production Environment
                client = storage.Client()
                bucket = client.get_bucket(settings.GS_BUCKET_NAME)
                blob = bucket.blob('kp_app/images/art4.jpg')
                blob.upload_from_string(
                    contact_image.read(),
                    content_type=contact_image.content_type
                )
                print(f"New contact image saved to GCS: {blob.public_url}")
            else:
                # Local Development Environment
                image_path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', 'art4.jpg')
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                with open(image_path, 'wb+') as destination:
                    for chunk in contact_image.chunks():
                        destination.write(chunk)
                print(f"New contact image saved to {image_path}")

        contact_page.save()

        # if the user changed the social media links, then the contact page will also need those updates
        blog_page.save()

        print("Contact Page settings updated with new user input and saved to the DB")
        
        return HttpResponseRedirect(reverse('contact'))
    
    except Exception as e:
        print(f"Error saving Contact Page settings: {e}")
        response = HttpResponse(status=400, content="Contact Page Settings update failed")
        return response


def contact_edit_home(request):
    # Get the existing contact page settings
    contact_page = ContactPageSettings.objects.first()
    
    # If no settings exist, create a new one with default values
    if not contact_page:
        contact_page = ContactPageSettings.objects.create(
            edu_address="address here",
            edu_phone="phone here",
            edu_email="email here",
            edu_facebook="facebook here",
            edu_instagram="instagram here",
            font="sans-serif",
            font_color="black",
            font_style="normal",
        )

    # if the user changed the social media links, then the contact page will also need those updates
    # Get the existing contact page settings
    blog_page = BlogPageSettings.objects.first()
    
    # If no settings exist, create a new one with default values
    if not blog_page:
        blog_page = BlogPageSettings.objects.create(
            blog_title="blgo title here",
            blog_text="blog text here",
            edu_facebook="facebook here",
            edu_instagram="instagram here",
            font="sans-serif",
            font_color="black",
            font_style="normal",
        )

    # Update fields only if new values are provided, otherwise just use the prev value
    contact_page.edu_address = request.POST.get('contact_address') or contact_page.edu_address
    contact_page.edu_phone = request.POST.get('contact_phone') or contact_page.edu_phone
    contact_page.edu_email = request.POST.get('contact_email') or contact_page.edu_email
    contact_page.edu_facebook = request.POST.get('contact_facebook') or contact_page.edu_facebook
    contact_page.edu_instagram = request.POST.get('contact_instagram') or contact_page.edu_instagram
    contact_page.font = request.POST.get('contact_font') or contact_page.font
    contact_page.font_color = request.POST.get('contact_font_color') or contact_page.font_color
    contact_page.font_style = request.POST.get('contact_font_style') or contact_page.font_style

    contact_image = request.FILES.get('contact_image')

    # if the user changed the social media links, then the contact page will also need those updates
    blog_page.edu_facebook = request.POST.get('contact_facebook') or blog_page.edu_facebook
    blog_page.edu_instagram = request.POST.get('contact_instagram') or blog_page.edu_instagram

    
    print(f"Updating Contact Page settings: {
        contact_page.edu_address, 
        contact_page.edu_phone, 
        contact_page.edu_email,
        contact_page.edu_facebook,
        contact_page.edu_instagram,
        contact_page.font,
        contact_page.font_color,
        contact_page.font_style,
    }, image: {'Provided' if contact_image else 'Not provided'}")
    
    try:
        if contact_image:
            if os.getenv("KP_PROD") == "true":
                # GCP Production Environment
                client = storage.Client()
                bucket = client.get_bucket(settings.GS_BUCKET_NAME)
                blob = bucket.blob('kp_app/images/art4.jpg')
                blob.upload_from_string(
                    contact_image.read(),
                    content_type=contact_image.content_type
                )
                print(f"New contact image saved to GCS: {blob.public_url}")
            else:
                # Local Development Environment
                image_path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', 'art4.jpg')
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                with open(image_path, 'wb+') as destination:
                    for chunk in contact_image.chunks():
                        destination.write(chunk)
                print(f"New contact image saved to {image_path}")

        contact_page.save()

        # if the user changed the social media links, then the contact page will also need those updates
        blog_page.save()

        print("Contact Page settings updated with new user input and saved to the DB")
        
        return HttpResponseRedirect(reverse('home'))  # Redirects to home page
    
    except Exception as e:
        print(f"Error saving Contact Page settings: {e}")
        response = HttpResponse(status=400, content="Contact Page Settings update failed")
        return response


def art_categories_page_edit(request):
    if request.method == 'POST':
        settings = ArtCategoryPageSettings.objects.first()
        if not settings:
            settings = ArtCategoryPageSettings.objects.create(
                font='sans-serif',
                font_color='black',
                font_style='normal',
                edu_email='default@email.com'
            )

        settings.font = request.POST.get('font', settings.font).lower()
        settings.font_color = request.POST.get('font_color', settings.font_color).lower()
        settings.font_style = request.POST.get('font_style', settings.font_style).lower()
        settings.edu_email = request.POST.get('email', settings.edu_email)

        try:
            settings.save()
            print("Art Category Page Settings successfully changed in the DB")
            return HttpResponseRedirect(reverse('art_categories'))
        except Exception as e:
            print(f"Error saving settings: {e}")
            response = HttpResponse(status=400, content="Art Category Page Settings update failed")
            return response
    
    return HttpResponse(status=405, content="the Art Category Page Edit view was not a POST")



def art1_page_edit(request):
    if request.method == 'POST':
        settings = Art1PageSettings.objects.first()
        if not settings:
            settings = Art1PageSettings.objects.create(
                font='sans-serif',
                font_color='black',
                font_style='normal',
                edu_email='default@email.com'
            )

        settings.font = request.POST.get('font', settings.font).lower()
        settings.font_color = request.POST.get('font_color', settings.font_color).lower()
        settings.font_style = request.POST.get('font_style', settings.font_style).lower()
        settings.edu_email = request.POST.get('email', settings.edu_email)

        try:
            settings.save()
            print("Art1 Page Settings successfully changed in the DB")
            return HttpResponseRedirect(reverse('art_categories'))
        except Exception as e:
            print(f"Error saving settings: {e}")
            response = HttpResponse(status=400, content="Art1 Page Settings update failed")
            return response
    
    return HttpResponse(status=405, content="the Art1 Page Edit view was not a POST")


def art2_page_edit(request):
    if request.method == 'POST':
        settings = Art2PageSettings.objects.first()
        if not settings:
            settings = Art2PageSettings.objects.create(
                font='sans-serif',
                font_color='black',
                font_style='normal',
                edu_email='default@email.com'
            )

        settings.font = request.POST.get('font', settings.font).lower()
        settings.font_color = request.POST.get('font_color', settings.font_color).lower()
        settings.font_style = request.POST.get('font_style', settings.font_style).lower()
        settings.edu_email = request.POST.get('email', settings.edu_email)

        try:
            settings.save()
            print("Art2 Page Settings successfully changed in the DB")
            return HttpResponse(status=200, content="Art 2 Page Settings successfully updated")
        except Exception as e:
            print(f"Error saving settings: {e}")
            response = HttpResponse(status=400, content="Art2 Page Settings update failed")
            return response
    
    return HttpResponse(status=405, content="the Art2 Page Edit view was not a POST")



def home_page_menu_edit(request):
    menu = MenuSettings.objects.first()
    if not menu:
        menu = MenuSettings.objects.create(
            font='sans-serif',
            font_color='black',
            font_style='normal'
        )

    menu.font = request.POST.get('menu_font', menu.font).lower()
    menu.font_color = request.POST.get('menu_font_color', menu.font_color).lower()
    menu.font_style = request.POST.get('menu_font_style', menu.font_style).lower()
    menu_image = request.FILES.get('menu_image')


    try:
        if menu_image:
            if os.getenv("KP_PROD") == "true":
                # GCP Production Environment
                client = storage.Client()
                bucket = client.get_bucket(settings.GS_BUCKET_NAME)
                blob = bucket.blob('kp_app/images/art5.jpg')
                blob.upload_from_string(
                    menu_image.read(),
                    content_type=menu_image.content_type
                )
                print(f"New menu image saved to GCS: {blob.public_url}")
            else:
                # Local Development Environment
                image_path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', 'art5.jpg')
                os.makedirs(os.path.dirname(image_path), exist_ok=True)  # Create directory if it doesn't exist
                with open(image_path, 'wb+') as destination:
                    for chunk in menu_image.chunks():
                        destination.write(chunk)
                print(f"New menu image saved to {image_path}")

        menu.save()
        print("Menu Settings successfully changed in the DB")
        return HttpResponseRedirect(reverse('home'))
    except Exception as e:
        print(f"Error saving Menu settings: {e}")
        response = HttpResponse(status=400, content="Menu Settings update failed")
        return response





def home_page_1_edit(request):
    home_page = HomePage1Settings.objects.first()
    if not home_page:
        home_page = HomePage1Settings.objects.create(
            title='Default Title',
            font='sans-serif',
            font_color='black',
            font_style='normal'
        )

    home_page.title = request.POST.get('title', home_page.title)
    home_page.font = request.POST.get('font', home_page.font).lower()
    home_page.font_color = request.POST.get('font_color', home_page.font_color).lower()
    home_page.font_style = request.POST.get('font_style', home_page.font_style).lower()

    background_image = request.FILES.get('background_image')
    
    try:
        if background_image:
            if os.getenv("KP_PROD") == "true":
                # GCP Production Environment
                client = storage.Client()
                bucket = client.get_bucket(settings.GS_BUCKET_NAME)
                blob = bucket.blob('kp_app/images/bg1.jpg')
                blob.upload_from_string(
                    background_image.read(),
                    content_type=background_image.content_type
                )
                print(f"New background image saved to GCS: {blob.public_url}")
            else:
                # Local Development Environment
                image_path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', 'bg1.jpg')
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                with open(image_path, 'wb+') as destination:
                    for chunk in background_image.chunks():
                        destination.write(chunk)
                print(f"New background image saved to {image_path}")

        home_page.save()
        print("Home Page 1 Settings successfully changed in the DB")
        return HttpResponseRedirect(reverse('home'))
    except Exception as e:
        print(f"Error saving Home Page 1 settings: {e}")
        response = HttpResponse(status=400, content="Home Page 1 Settings update failed")
        return response

def home_page_2_edit(request):
    home_page_2 = HomePage2Settings.objects.first()
    if not home_page_2:
        home_page_2 = HomePage2Settings.objects.create(
            homepage2_text='Default Text',
            font='sans-serif',
            font_color='black',
            font_style='normal'
        )

    home_page_2.homepage2_text = request.POST.get('homepage2_text', home_page_2.homepage2_text)
    home_page_2.font = request.POST.get('font', home_page_2.font).lower()
    home_page_2.font_color = request.POST.get('font_color', home_page_2.font_color).lower()
    home_page_2.font_style = request.POST.get('font_style', home_page_2.font_style).lower()

    homepage_2_image_1 = request.FILES.get('homepage_2_image_1')
    
    try:
        if homepage_2_image_1:
            if os.getenv("KP_PROD") == "true":
                # GCP Production Environment
                client = storage.Client()
                bucket = client.get_bucket(settings.GS_BUCKET_NAME)
                blob = bucket.blob('kp_app/images/art1.jpg')
                blob.upload_from_string(
                    homepage_2_image_1.read(),
                    content_type=homepage_2_image_1.content_type
                )
                print(f"New image saved to GCS: {blob.public_url}")
            else:
                # Local Development Environment
                image_path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', 'art1.jpg')
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                with open(image_path, 'wb+') as destination:
                    for chunk in homepage_2_image_1.chunks():
                        destination.write(chunk)
                print(f"New image saved to {image_path}")

        home_page_2.save()
        print("Home Page 2 Settings successfully changed in the DB")
        return HttpResponseRedirect(reverse('home'))
    except Exception as e:
        print(f"Error saving Home Page 2 settings: {e}")
        response = HttpResponse(status=400, content="Home Page 2 Settings update failed")
        return response

def home_page_3_edit(request):
    home_page_3 = HomePage3Settings.objects.first()
    if not home_page_3:
        home_page_3 = HomePage3Settings.objects.create(
            homepage3_text='Default Text',
            font='sans-serif',
            font_color='black',
            font_style='normal'
        )

    home_page_3.homepage3_text = request.POST.get('homepage3_text', home_page_3.homepage3_text)
    home_page_3.font = request.POST.get('font', home_page_3.font).lower()
    home_page_3.font_color = request.POST.get('font_color', home_page_3.font_color).lower()
    home_page_3.font_style = request.POST.get('font_style', home_page_3.font_style).lower()

    try:
        home_page_3.save()
        print("Home Page 3 Settings successfully changed in the DB")
        return HttpResponseRedirect(reverse('home'))
    except Exception as e:
        print(f"Error saving Home Page 3 settings: {e}")
        response = HttpResponse(status=400, content="Home Page 3 Settings update failed")
        return response

def home_page_4_edit(request):
    home_page_4 = HomePage4Settings.objects.first()
    if not home_page_4:
        home_page_4 = HomePage4Settings.objects.create(
            homepage4_text='Default Text',
            font='sans-serif',
            font_color='black',
            font_style='normal'
        )

    home_page_4.homepage4_text = request.POST.get('homepage4_text', home_page_4.homepage4_text)
    home_page_4.font = request.POST.get('homepage4_font', home_page_4.font).lower()
    home_page_4.font_color = request.POST.get('homepage4_font_color', home_page_4.font_color).lower()
    home_page_4.font_style = request.POST.get('homepage4_font_style', home_page_4.font_style).lower()

    homepage_4_image_1 = request.FILES.get('homepage_4_image_1')

    try:
        if homepage_4_image_1:
            if os.getenv("KP_PROD") == "true":
                # GCP Production Environment
                client = storage.Client()
                bucket = client.get_bucket(settings.GS_BUCKET_NAME)
                blob = bucket.blob('kp_app/images/art3.jpg')
                blob.upload_from_string(
                    homepage_4_image_1.read(),
                    content_type=homepage_4_image_1.content_type
                )
                print(f"New image saved to GCS: {blob.public_url}")
            else:
                # Local Development Environment
                image_path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', 'art3.jpg')
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                with open(image_path, 'wb+') as destination:
                    for chunk in homepage_4_image_1.chunks():
                        destination.write(chunk)
                print(f"New image saved to {image_path}")

        home_page_4.save()
        print("Home Page 4 Settings successfully changed in the DB")
        return HttpResponseRedirect(reverse('home'))
    except Exception as e:
        print(f"Error saving Home Page 4 settings: {e}")
        response = HttpResponse(status=400, content="Home Page 4 Settings update failed")
        return response


def get_navbar(request):
    return render(request, 'navbar.html')


def get_navbar_home(request):
    return render(request, 'navbar_home.html')


def get_navbar_blog_lg(request):
    return render(request, 'navbar_blog.html')


def get_navbar_blog_sm(request):
    return render(request, 'navbar_blog_sm.html')
