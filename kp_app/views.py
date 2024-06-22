from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from .models import UserCredential, Art1PageSettings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password, check_password
from .forms import LoginForm
from .forms import RegistrationForm
import os
from dotenv import load_dotenv


load_dotenv()

class Tester:
    def __init__(self, info="woof", ready=False):
        self.info = info
        self.ready = ready

test1 = Tester("meow", False)
test2 = Tester("nya", True)


def home(request):
    if request.headers.get('HX-Request') == 'true':
        print("home page came from HTMX")
        return render(request, "home_content.html")
    else:
        print("home page did NOT come from HTMX")
        return render(request, "home.html")

def contact(request):
    if request.headers.get('HX-Request') == 'true':
        print("contact page came from HTMX")
        return render(request, "contact_content.html")
    else:
        print("contact page did NOT come from HTMX")
        return render(request, "contact.html")

def art1(request):
    # Fetch the page settings from the DB
    # Assuming you want the first (or only) set of settings
    try:
        settings = Art1PageSettings.objects.first()
        page_settings = {
            'font': settings.font,
            'font_color': settings.font_color,
            'edu_email': settings.edu_email,
        }
    except Art1PageSettings.DoesNotExist:
        # Provide default values if no settings are found
        page_settings = {
            'font': 'sans-serif',
            'font_color': '#000000',
            'edu_email': 'jojohoughton22@gmail.com',
        }
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

        return render(request, 'art2_content.html', {"image_obj": image_obj})
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

        return render(request, 'art2.html', {"image_obj": image_obj})


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





