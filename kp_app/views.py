from django.shortcuts import render
#from .models import Test

# Create your views here.

class Tester:
    def __init__(self, info="woof", ready=False):
        self.info = info
        self.ready = ready

test1 = Tester("meow", False)
test2 = Tester("nya", True)

def home(request):
    #items = Test.objects.all() 
    return render(request, "home.html", {"tests": [test1, test2]})

