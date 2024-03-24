from django.urls import path
from . import views


# these are URL patterns that will connect to a specific URL/View
# these also need to be added to the urls.py file in the main proj root dir
urlpatterns = [
        # this says: when we're at the "/" (root) URL extension, call this home func
        path("", views.home, name="home"),
        path("send_email", views.send_email, name="send_email"),
        ]



