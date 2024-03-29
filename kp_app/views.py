from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from .models import Test
from .forms import EmailForm

class Tester:
    def __init__(self, info="woof", ready=False):
        self.info = info
        self.ready = ready

test1 = Tester("meow", False)
test2 = Tester("nya", True)


def home(request):
    #items = Test.objects.all() 
    return render(request, "home.html", {"tests": [test1, test2]})


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



