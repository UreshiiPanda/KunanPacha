from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.urls import reverse
from .models import UserCredential, Art1PageSettings, Art2PageSettings, HomePage1Settings, HomePage2Settings
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

    if not home_page_1_settings:
        # If no settings exist yet in the DB, create a default one
        home_page_1_settings = HomePage1Settings.objects.create(
            title='Edu Suarez',
            #background_image=os.path.join("static/kp_app/images/bg1.jpg")
        )
    if not home_page_2_settings:
        # If no settings exist yet in the DB, create a default one
        home_page_2_settings = HomePage2Settings.objects.create(
            homepage2_text='Text for home page 2 here',
            #homepage_2_image_1=os.path.join("static/kp_app/images/bg1.jpg")
        )


    page_settings = {
        "title": home_page_1_settings.title,
        "background_image": os.path.join("static/kp_app/images/bg1.jpg"),
        "homepage2_text": home_page_2_settings.homepage2_text,
        "homepage_2_image_1": os.path.join("static/kp_app/images/bg1.jpg")
        }


    # Now that there is for sure a settings object, set the vars to pass into template
    print(f"current home_page_1 settings coming into the home view: {home_page_1_settings}")
    print(f"current home_page_2 settings coming into the home view: {home_page_2_settings}")

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
            font_color='#000000',
            edu_email='jojohoughton22@gmail.com'
        )

    # Now that there is for sure a settings object, set the vars to pass into template
    page_settings = {
        'font': settings.font,
        'font_color': settings.font_color,
        'edu_email': settings.edu_email,
    }
    print(f"current page settings coming into the art1 view: {page_settings}")

    if request.headers.get('HX-Request') == 'true':
        print("art1 page came from HTMX")
        images_dir = os.path.join('static/kp_app/images') 
        images = os.listdir(images_dir)
        return render(request, "art1_content.html", {"images": images, "page_settings": page_settings})
    else:
        print("art1 page did NOT come from HTMX")
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
            font_color='#000000',
            edu_email='jojohoughton22@gmail.com'
        )

    # Now that there is for sure a settings object, set the vars to pass into template
    page_settings = {
        'font': settings.font,
        'font_color': settings.font_color,
        'edu_email': settings.edu_email,
    }
    print(f"current page settings coming into the art2 view: {page_settings}")


    if request.headers.get('HX-Request') == 'true':
        print("art2 page came from HTMX")
        # mocking the image locally 
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
        # mocking the image locally 
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




def art1_page_edit(request):
    if request.method == 'POST':
        font = request.POST.get('font').lower()
        font_color = request.POST.get('font_color').lower()
        edu_email = request.POST.get('email')
        print(f"incoming user settings for art1 page: font: {font}, font_color: {font_color}, email: {edu_email}")
        try:
            # Try to get the existing record
            # there should only be 1 record for this, cuz the page settings are
            # always replaced when the user input is valid
            settings = Art1PageSettings.objects.first()
            if settings:
               # # If a record exists, update it
                settings.font = font
                settings.font_color = font_color
                settings.edu_email = edu_email
                settings.save()
                print("new art page settings from user input, new settings have been saved to the DB")
            else:
                # If no record exists yet, create a new one
                print("art page settings doesn't exist in DB yet, creating a new one")
                Art1PageSettings.objects.create(
                    font=font,
                    font_color=font_color,
                    edu_email=edu_email
                )
           
            print("Art1 Page Settings successfully changed in the DB")
            return HttpResponseRedirect(reverse('art1'))
            #return render(request, "art1_content.html")
        except Exception as e:
            print(f"Error saving settings: {e}")  # Log the error
            print("Art1 Page Settings update failed")
            response = HttpResponse(status=400, content="Art1 Page Settings update failed")  # Bad request
            return response
            #return render(request, "art1.html")
    
    return HttpResponse(status=405, content="the Art1 Page Edit view was not a POST")  # Method not allowed


def art2_page_edit(request):
    if request.method == 'POST':
        font = request.POST.get('font').lower()
        font_color = request.POST.get('font_color').lower()
        edu_email = request.POST.get('email')
        print(f"incoming user settings for art1 page: font: {font}, font_color: {font_color}, email: {edu_email}")
        try:
            # Try to get the existing record
            # there should only be 1 record for this, cuz the page settings are
            # always replaced when the user input is valid
            settings = Art2PageSettings.objects.first()
            if settings:
               # # If a record exists, update it
                settings.font = font
                settings.font_color = font_color
                settings.edu_email = edu_email
                settings.save()
                print("new art page 2 settings from user input, new settings have been saved to the DB")
            else:
                # If no record exists yet, create a new one
                print("art page 2 settings doesn't exist in DB yet, creating a new one")
                Art2PageSettings.objects.create(
                    font=font,
                    font_color=font_color,
                    edu_email=edu_email
                )
           
            print("Art2 Page Settings successfully changed in the DB")
            return HttpResponseRedirect(reverse('art2'))
        except Exception as e:
            print(f"Error saving settings: {e}")  # Log the error
            print("Art2 Page Settings update failed")
            response = HttpResponse(status=400, content="Art2 Page Settings update failed")  # Bad request
            return response
    
    return HttpResponse(status=405, content="the Art2 Page Edit view was not a POST")  # Method not allowed




def home_page_1_edit(request):
    title = request.POST.get('title')
    background_image = request.FILES.get('background_image')
    
    print(f"Incoming settings for home page 1: title: {title}, background image: {'Provided' if background_image else 'Not provided'}")
    
    try:
        # Try to get the existing record
        home_page = HomePage1Settings.objects.first()
        if home_page:
            # If a record exists, update it
            home_page.title = title
            if background_image:
                home_page.background_image = background_image
            home_page.save()
            print("Home page 1 settings updated with new user input and saved to the DB")
        else:
            # If no record exists yet, create a new one
            print("Home page 1 settings don't exist in DB yet, creating a new one")
            home_page = HomePage1Settings.objects.create(
                title=title,
                background_image=background_image
            )
        
        print("Home Page 1 Settings successfully changed in the DB")
        return HttpResponseRedirect(reverse('home'))  # Assuming you have a 'home' URL name
    
    except Exception as e:
        print(f"Error saving Home Page 1 settings: {e}")  # Log the error
        print("Home Page 1 Settings update failed")
        response = HttpResponse(status=400, content="Home Page 1 Settings update failed")  # Bad request
        return response




def home_page_2_edit(request):
    homepage2_text = request.POST.get('homepage2_text')
    homepage_2_image_1 = request.FILES.get('homepage_2_image_1')
    
    print(f"Incoming settings for home page 2: text: {homepage2_text}, image: {'Provided' if homepage_2_image_1 else 'Not provided'}")
    
    try:
        # Try to get the existing record
        home_page_2 = HomePage2Settings.objects.first()
        if home_page_2:
            # If a record exists, update it
            home_page_2.text = homepage2_text
            if homepage_2_image_1:
                home_page_2.image = homepage_2_image_1
            home_page_2.save()
            print("Home page 2 settings updated with new user input and saved to the DB")
        else:
            # If no record exists yet, create a new one
            print("Home page 2 settings don't exist in DB yet, creating a new one")
            home_page_2 = HomePage2Settings.objects.create(
                text=homepage2_text,
                image=homepage_2_image_1
            )
        
        print("Home Page 2 Settings successfully changed in the DB")
        return HttpResponseRedirect(reverse('home'))  # Assuming you have a 'home' URL name
    
    except Exception as e:
        print(f"Error saving Home Page 2 settings: {e}")  # Log the error
        print("Home Page 2 Settings update failed")
        response = HttpResponse(status=400, content="Home Page 2 Settings update failed")  # Bad request
        return response



