from django.urls import path
from . import views


# these are URL patterns that will connect to a specific URL/View
# these also need to be added to the urls.py file in the main proj root dir
urlpatterns = [
        # this says: when we're at the "/" (root) URL extension, call this home func
        path("", views.home, name="home"),
        path("contact", views.contact, name="contact"),
        path("art1", views.art1, name="art1"),
        #path('art2/<int:image_id>/', views.art2, name='art2'),
        path('art2', views.art2, name='art2'),
        path("send_email", views.send_email, name="send_email"),
        path('login', views.login_admin, name='login_admin'),
        ]



