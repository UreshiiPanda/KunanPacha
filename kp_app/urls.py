from django.conf.urls import include
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .views import register

# these are URL patterns that will connect to a specific URL/View
# these also need to be added to the urls.py file in the main proj root dir
urlpatterns = [
    # this says: when we're at the "/" (root) URL extension, call this home func
    path("", views.home, name="home"),
    path("contact", views.contact, name="contact"),
    path("art1", views.art1, name="art1"),
    path("add_art", views.add_art, name="add_art"),
    path("art2/<int:artwork_id>/", views.art2, name="art2"),
    path("edit_artwork/<int:artwork_id>", views.edit_artwork, name="edit_artwork"),
    path(
        "delete_artwork/<int:artwork_id>/", views.delete_artwork, name="delete_artwork"
    ),
    path("art-categories", views.art_categories, name="art_categories"),
    path("send_email", views.send_email, name="send_email"),
    path("login_admin", views.login_admin, name="login_admin"),
    path("register/", register, name="register"),
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # path("accounts/", include("django.contrib.auth.urls")),
    path("art1_page_edit", views.art1_page_edit, name="art1_page_edit"),
    path("art2_page_edit", views.art2_page_edit, name="art2_page_edit"),
    path("home_page_1_edit", views.home_page_1_edit, name="home_page_1_edit"),
    path("home_page_2_edit", views.home_page_2_edit, name="home_page_2_edit"),
    path("home_page_3_edit", views.home_page_3_edit, name="home_page_3_edit"),
    path("home_page_4_edit", views.home_page_4_edit, name="home_page_4_edit"),
    path("home_page_menu_edit", views.home_page_menu_edit, name="home_page_menu_edit"),
    path("contact_edit_home", views.contact_edit_home, name="contact_edit_home"),
    path("contact_edit", views.contact_edit, name="contact_edit"),
    path("blog/", views.blog, name="blog"),
    path("blog/<int:page>/", views.blog, name="blog"),
    path("blog2/<int:post_id>/", views.blog2, name="blog2"),
    path("blog_page_edit", views.blog_page_edit, name="blog_page_edit"),
    path("add_blog", views.add_blog, name="add_blog"),
    path("edit_blog/<int:blog_id>", views.edit_blog, name="edit_blog"),
    path("delete_blog/<int:blog_id>/", views.delete_blog, name="delete_blog"),
    path("get-navbar/", views.get_navbar, name="get_navbar"),
    path("get-navbar-home/", views.get_navbar_home, name="get_navbar_home"),
    path("get-navbar-blog_lg/", views.get_navbar_blog_lg, name="get_navbar_blog_lg"),
    path("get-navbar-blog_sm/", views.get_navbar_blog_sm, name="get_navbar_blog_sm"),
]
