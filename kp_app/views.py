from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.urls import reverse
from .models import UserCredential, Art1PageSettings, Art2PageSettings, HomePage1Settings, HomePage2Settings, HomePage3Settings, HomePage4Settings, ContactPageSettings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.template.loader import render_to_string
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
    if request.headers.get('HX-Request') == 'true':
        print("contact page came from HTMX")
        return render(request, "contact_content.html")
    else:
        print("contact page did NOT come from HTMX")
        return render(request, "contact.html")


def art1(request):
    # Fetch the page settings from the DB
    # First check if any Art1PageSettings object exists
    settings = Art1PageSettings.objects.first()

    if not settings:
        # If no settings exist yet in the DB, create a default one
        settings = Art1PageSettings.objects.create(
            font='sans-serif',
            font_color='black',
            font_style='normal',
            edu_email='jojohoughton22@gmail.com'
        )

    # Now that there is for sure a settings object, set the vars to pass into template
    page_settings = {
        'font': settings.font,
        'font_color': settings.font_color,
        'font_style': settings.font_style,
        'edu_email': settings.edu_email,
    }
    print(f"current page settings coming into the art1 view: {page_settings}")

    if request.headers.get('HX-Request') == 'true':
        print("art1 page came from HTMX")

        if os.getenv("KP_PROD") == "true":
            print("in Art1 view in views.py, in PROD env, getting images from GCP")
        else:
            print("in Art1 view in views.py, in DEV env, getting images from local files")
            images_dir = os.path.join('static/kp_app/images') 
            images = os.listdir(images_dir)

        return render(request, "art1_content.html", {"images": images, "page_settings": page_settings})
    else:
        print("art1 page did NOT come from HTMX")
        if os.getenv("KP_PROD") == "true":
            print("in Art1 view in views.py, in PROD env, getting images from GCP")
        else:
            print("in Art1 view in views.py, in DEV env, getting images from local files")
            images_dir = os.path.join('static/kp_app/images') 
            images = os.listdir(images_dir)

        return render(request, "art1.html", {"images": images, "page_settings": page_settings})


# def art2(request, image_id):
def art2(request):
    # if the image comes from a DB
    #image = get_object_or_404(Image, id=image_id)
    #context = {
    #    'image': image,
    #    'image_url': image.image.url,
    #    'title': image.title,
    #    'description': image.description,
    #    'price': image.price,
    #}

    # Fetch the page settings from the DB
    # First check if any Art1PageSettings object exists
    settings = Art2PageSettings.objects.first()

    if not settings:
        # If no settings exist yet in the DB, create a default one
        settings = Art2PageSettings.objects.create(
            font='sans-serif',
            font_color='black',
            font_style='normal',
            edu_email='jojohoughton22@gmail.com'
        )

    # Now that there is for sure a settings object, set the vars to pass into template
    page_settings = {
        'font': settings.font,
        'font_color': settings.font_color,
        'font_style': settings.font_style,
        'edu_email': settings.edu_email,
    }
    print(f"current page settings coming into the art2 view: {page_settings}")


    if request.headers.get('HX-Request') == 'true':
        print("art2 page came from HTMX")

        if os.getenv("KP_PROD") == "true":
            # if we're in PROD env, grab images from GCP
            print("in Art2 view in views.py, in PROD env, getting images from GCP")
        else:
            print("in Art2 view in views.py, in DEV env, getting images from local files")
            images_dir = os.path.join('static/kp_app/images')      
            image_obj = {
                'image': os.listdir(images_dir)[0],
                'title': "Image Title",
                'desc': "Lorem ipsum dolor sit amet, consectetur estor adipi isicing elit, sed do eiusmod tempor este uterre incididui unt ut labore et dolore magna aliquaas. Ut enim ad minim veniam nostrud desto exercitation est ullamco laboris nisi ut se aliquip ex ea commodos consequat. Duis aute irure et dolor in reprehender itinse",
                'print_price': "40",
                'original_price': "100"
            }

        return render(request, 'art2_content.html', {"image_obj": image_obj, "page_settings": page_settings})
    else:
        print("art2 page did NOT come from HTMX")

        if os.getenv("KP_PROD") == "true":
            # if we're in PROD env, grab images from GCP
            print("in Art2 view in views.py, in PROD env, getting images from GCP")
        else:
            print("in Art2 view in views.py, in DEV env, getting images from local files")
            images_dir = os.path.join('static/kp_app/images')      
            image_obj = {
                'image': os.listdir(images_dir)[0],
                'title': "Image Title",
                'desc': "Lorem ipsum dolor sit amet, consectetur estor adipi isicing elit, sed do eiusmod tempor este uterre incididui unt ut labore et dolore magna aliquaas. Ut enim ad minim veniam nostrud desto exercitation est ullamco laboris nisi ut se aliquip ex ea commodos consequat. Duis aute irure et dolor in reprehender itinse",
                'print_price': "40",
                'original_price': "100"
            }

        return render(request, 'art2.html', {"image_obj": image_obj, "page_settings": page_settings})


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

