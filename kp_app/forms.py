from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import BlogPost
from django_summernote.fields import SummernoteTextFormField, SummernoteTextField

class BlogPostForm(forms.Form):
    description = SummernoteTextFormField()

#class BlogPostForm(forms.ModelForm):
#    description = SummernoteTextField()
#
#    class Meta:
#        model = BlogPost
#        fields = ['description']

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class EmailForm(forms.Form):
    name = forms.CharField(label="name", max_length=100)
    email = forms.CharField(label="email", max_length=100)
    msg = forms.CharField(label="msg", max_length=5000)


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
