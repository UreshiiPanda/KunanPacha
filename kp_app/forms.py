from django import forms


class EmailForm(forms.Form):
    name = forms.CharField(label="name", max_length=100)
    email = forms.CharField(label="email", max_length=100)
    msg = forms.CharField(label="msg", max_length=5000)


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
