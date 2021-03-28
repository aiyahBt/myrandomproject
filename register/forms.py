from django import forms
from django.views import generic
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

# class EditForm(generic.CreateView):
#     email = forms.EmailField()
#
#     class Meta:
#         model = User
#         fields = ["username", "email", "password1", "password2"]


# class EditForm(generic.CreateView):
#     form_class = UserChangeForm
#     template_name = 'registration/edit_profile.html'
#     success_url = '/home'