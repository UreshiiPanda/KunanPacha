from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError
from django.core.files.storage import default_storage
from google.cloud import storage
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from .models import UserCredential, Art1PageSettings, Art2PageSettings, HomePage1Settings, HomePage2Settings, HomePage3Settings, HomePage4Settings, ContactPageSettings, MenuSettings, Artwork
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
import json
from .forms import LoginForm
from .forms import RegistrationForm
import os
from dotenv import load_dotenv

load_dotenv()




def home(request):
    home_page_1_settings = HomePage1Settings.objects.first()
    home_page_2_settings = HomePage2Settings.objects.first()
    home_page_3_settings = HomePage3Settings.objects.first()
    home_page_4_settings = HomePage4Settings.objects.first()
    contact_page_settings = ContactPageSettings.objects.first()
    menu_settings = MenuSettings.objects.first()

    if not home_page_1_settings:
        home_page_1_settings = HomePage1Settings.objects.create(
            title='Edu Suarez',
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

    page_settings = {
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

    if request.headers.get('HX-Request') == 'true':
        print("contact page came from HTMX")
        return render(request, "contact_content.html", {"page_settings": page_settings})
    else:
        print("contact page did NOT come from HTMX")
        return render(request, "contact.html", {"page_settings": page_settings})



def art1(request):
    # Fetch the page settings from the DB
    page_settings = Art1PageSettings.objects.first()
    if not page_settings:
        page_settings = Art1PageSettings.objects.create(
            font='sans-serif',
            font_color='black',
            font_style='normal',
            edu_email='jojohoughton22@gmail.com'
        )

    # Fetch artworks from the database
    artworks = Artwork.objects.all().order_by('-created_at')
     
    ## Prepare artwork data
    #artwork_data = []
    #for artwork in artworks:
    #    # on the art1 page, we only need image1, so we do not retrieve the other images until the user goes
    #    # to art2 page
    #    if os.getenv("KP_PROD") == "false":
    #        # note that the full url is constructed here, so the url stem is thus removed from the retrieval in the template
    #        image_url = os.path.join(settings.STATIC_URL, 'kp_app/images', artwork.image1_filename)
    #        print(f"here is image_url: {image_url}")
    #    else:
    #        image_url = f'{settings.STATIC_URL}{artwork.image1_filename}'
    #    artwork_data.append({
    #        'id': artwork.id,
    #        'title': artwork.title,
    #        'original_price': artwork.original_price,
    #        'print_price': artwork.print_price,
    #        'description': artwork.description,
    #        'dimensions': artwork.dimensions,
    #        'image_url': image_url,
    #        'created_at': artwork.created_at,
    #        'updated_at': artwork.updated_at,
    #    })


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
            image_base_url = settings.STATIC_URL
            image_urls = [
                f'{image_base_url}{artwork.image1_filename}',
                f'{image_base_url}{artwork.image2_filename}' if artwork.image2_filename else None,
                f'{image_base_url}{artwork.image3_filename}' if artwork.image3_filename else None,
                f'{image_base_url}{artwork.image4_filename}' if artwork.image4_filename else None,
            ]

        artwork_data.append({
            'id': artwork.id,
            'title': artwork.title,
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


    if request.headers.get('HX-Request') == 'true':
        print("art1 page came from HTMX")
        return render(request, "art1_content.html", {"artworks": artwork_data, "page_settings": page_settings})
    else:
        print("art1 page did NOT come from HTMX")
        return render(request, "art1.html", {"artworks": artwork_data, "page_settings": page_settings})




def add_art(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        original_price = request.POST.get('original_price')
        print_price = request.POST.get('print_price')
        description = request.POST.get('description')
        dimensions = request.POST.get('dimensions')
        images = [request.FILES.get(f'image{i}') for i in range(1, 5)]

        # make sure there is at least 1 image, the rest are optional
        if title and original_price and print_price and description and dimensions and images[0]:
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
                        blob = bucket.blob(f'images/{filename}')
                        blob.upload_from_file(image)

            # Create Artwork object
            # the create() func also performs .save() so we don't need to do artwork.save() after this
            artwork = Artwork.objects.create(
                title=title,
                original_price=original_price,
                print_price=print_price,
                description=description,
                dimensions=dimensions,
                image1_filename=filenames[0],
                image2_filename=filenames[1] if len(filenames) > 1 else None,
                image3_filename=filenames[2] if len(filenames) > 2 else None,
                image4_filename=filenames[3] if len(filenames) > 3 else None
            )

            return HttpResponseRedirect(reverse('art1'))
        else:
            print('from Add Art modal, All required fields must be filled and at least one image uploaded')
            return HttpResponse('from Add Art modal, All required fields must be filled and at least one image uploaded', status=400)

    return render(request, 'add_art.html')





#@require_http_methods(["PUT"])
# the PUT was not detecting the FILES for some reason, but the POST works
def edit_artwork(request, artwork_id):
    print(artwork_id)
    print(request.POST.get('description'))
    print(request.POST.get('removed3'))
    if 'image1' in request.FILES:
        print(f"image1: {request.FILES['image1']}")
    if 'image2' in request.FILES:
        print(f"image2: {request.FILES['image2']}")
    if 'image3' in request.FILES:
        print(f"image3: {request.FILES['image3']}")
    if 'image4' in request.FILES:
        print(f"image4: {request.FILES['image4']}")
    for filename, file in request.FILES.items():
        print(f"Filename: {filename}")
        print(f"File: {file}")
        print(f"File size: {file.size}")
        print(f"Content type: {file.content_type}")
    artwork = get_object_or_404(Artwork, id=artwork_id)
    print("in edit_artwork 2")


    # Update the basic fields
    # or leave them the same if the user didn't supply a new value
    artwork.title = request.POST.get('title', artwork.title)
    artwork.original_price = request.POST.get('original_price', artwork.original_price)
    artwork.print_price = request.POST.get('print_price', artwork.print_price)
    artwork.description = request.POST.get('description', artwork.description)
    artwork.dimensions = request.POST.get('dimensions', artwork.dimensions)

    # Handle image updates
    for i in range(1, 5):
        image_field = f'image{i}'
        if image_field in request.FILES:
            print("in edit_artwork 3")
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
                blob = bucket.blob(f'images/{filename}')
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
                    blob = bucket.blob(f'images/{old_filename}')
                    if blob.exists():
                        blob.delete()

            # Update the filename in the model
            setattr(artwork, f'image{i}_filename', filename)

    # check if the user deleted any of the files via the removed input field that was
    # made to cirumvent Alpine issues
    # NOTE that image1 is not allowed to be removed by the user in the UI because an Artwork must
    # have at least 1 image
    for i in range(1, 5):
        if request.POST.get(f'removed{i}') == "true":
            print(f'removing image {i} from artwork {artwork.title}')
            setattr(artwork, f'image{i}_filename', None)
            


    artwork.save()
    print("in edit_artwork 4")
    return HttpResponseRedirect(reverse('art1'))
    #else:
    #    # If it's not a PUT request, just render the art1 page
    #    return HttpResponseRedirect(reverse('art1'))


@require_http_methods(["DELETE"])
def delete_artwork(request, artwork_id):
    artwork = get_object_or_404(Artwork, id=artwork_id)
    artwork.delete()
    return HttpResponseRedirect(reverse('art1'))







def art2(request, artwork_id):
    # note that Django automatically adds an ID to every object in the models
    artwork = get_object_or_404(Artwork, id=artwork_id)
    
    page_settings = Art2PageSettings.objects.first()
    if not page_settings:
        page_settings = Art2PageSettings.objects.create(
            font='sans-serif',
            font_color='black',
            font_style='normal',
            edu_email='default@email.com'
        )


    # Determine the environment and set image URLs accordingly
    if os.getenv("KP_PROD") == "true":
        # GCP environment
        image_base_url = settings.STATIC_URL
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

    context = {
        "image_obj": image_obj,
        "page_settings": page_settings
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
            # Save the image to the specific location
            image_path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', 'art4.jpg')
            with open(image_path, 'wb+') as destination:
                for chunk in contact_image.chunks():
                    destination.write(chunk)
            print(f"New background image saved to {image_path}")

        contact_page.save()
        print("Contact Page settings updated with new user input and saved to the DB")
        
        return HttpResponseRedirect(reverse('home'))  # Assuming you have a 'home' URL name
    
    except Exception as e:
        print(f"Error saving Contact Page settings: {e}")  # Log the error
        print("Contact Page Settings update failed")
        response = HttpResponse(status=400, content="Contact Page Settings update failed")  # Bad request
        return response




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
            # Save the image to the specific location
            image_path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', 'art4.jpg')
            with open(image_path, 'wb+') as destination:
                for chunk in contact_image.chunks():
                    destination.write(chunk)
            print(f"New background image saved to {image_path}")

        contact_page.save()
        print("Contact Page settings updated with new user input and saved to the DB")
        
        return HttpResponseRedirect(reverse('contact'))  # Assuming you have a 'home' URL name
    
    except Exception as e:
        print(f"Error saving Contact Page settings: {e}")  # Log the error
        print("Contact Page Settings update failed")
        response = HttpResponse(status=400, content="Contact Page Settings update failed")  # Bad request
        return response





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
            return HttpResponseRedirect(reverse('art1'))
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
            return HttpResponseRedirect(reverse('art2'))
        except Exception as e:
            print(f"Error saving settings: {e}")
            response = HttpResponse(status=400, content="Art2 Page Settings update failed")
            return response
    
    return HttpResponse(status=405, content="the Art2 Page Edit view was not a POST")


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
            image_path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', 'bg1.jpg')
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
            image_path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', 'art1.jpg')
            with open(image_path, 'wb+') as destination:
                for chunk in homepage_2_image_1.chunks():
                    destination.write(chunk)
            print(f"New background image saved to {image_path}")

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
            image_path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', 'art3.jpg')
            with open(image_path, 'wb+') as destination:
                for chunk in homepage_4_image_1.chunks():
                    destination.write(chunk)
            print(f"New background image saved to {image_path}")

        home_page_4.save()
        print("Home Page 4 Settings successfully changed in the DB")
        return HttpResponseRedirect(reverse('home'))
    except Exception as e:
        print(f"Error saving Home Page 4 settings: {e}")
        response = HttpResponse(status=400, content="Home Page 4 Settings update failed")
        return response



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
            image_path = os.path.join(settings.BASE_DIR, 'kp_app', 'static', 'kp_app', 'images', 'art5.jpg')
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

