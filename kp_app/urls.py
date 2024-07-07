from django.urls import path
from django.conf.urls import include
from . import views
from .views import register
from django.contrib.auth import views as auth_views


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
        path('login_admin', views.login_admin, name='login_admin'),
        path('register/', register, name='register'),
        path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
        path('logout/', auth_views.LogoutView.as_view(), name='logout'),
        #path("accounts/", include("django.contrib.auth.urls")),
        path("art1_page_edit", views.art1_page_edit, name="art1_page_edit"),
        path("art2_page_edit", views.art2_page_edit, name="art2_page_edit"),
        path("home_page_1_edit", views.home_page_1_edit, name="home_page_1_edit"),
        path("home_page_2_edit", views.home_page_2_edit, name="home_page_2_edit"),
        path("home_page_3_edit", views.home_page_3_edit, name="home_page_3_edit"),
        path("home_page_4_edit", views.home_page_4_edit, name="home_page_4_edit"),
        path("contact_edit", views.contact_edit, name="contact_edit"),
        ]



