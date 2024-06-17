from django.urls import path
from django.conf.urls import include
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
        path("accounts/", include("django.contrib.auth.urls")),
        # this includes the following URL patterns into your app:
        #accounts/login/ [name='login']
        #accounts/logout/ [name='logout']
        #accounts/password_change/ [name='password_change']
        #accounts/password_change/done/ [name='password_change_done']
        #accounts/password_reset/ [name='password_reset']
        #accounts/password_reset/done/ [name='password_reset_done']
        #accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
        #accounts/reset/done/ [name='password_reset_complete']
        ]



