from django import forms
from django.views import generic
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]




class AddressForm(forms.Form):
    #your_name = forms.CharField(label='Your name', max_length=100)
    address_str = forms.CharField(label='Address', max_length=200)
    number = forms.CharField(label='Number', max_length=10)
    street = forms.CharField(label='Street', max_length=100)
    sub_district = forms.CharField(label='Sub district', max_length=100)
    district = forms.CharField(label='District', max_length=100)
    province = forms.CharField(label='Province', max_length=100)
    postal_code = forms.IntegerField(label='Postal code')


# class AddressForm(forms.Form):
#     number = forms.IntegerField()


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