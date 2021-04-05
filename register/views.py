from django.shortcuts import render

from user.utilityFunction import validate_matching, redirect_to_home_something_went_wrong
from django.db import IntegrityError, transaction

from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.views import generic
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from .models import Address
from .forms import AddressForm

# Create your views here.
def register(response):
    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():
            form.save()

        return redirect("/home")
    else:
        form = RegisterForm()

    return render(response, "register/register.html", {"form":form})

class CustomFormForUserEditView(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

class UserEditView(generic.UpdateView):
    form_class = CustomFormForUserEditView
    template_name = 'registration/edit_profile.html'
    success_url = reverse_lazy('myApp:home')

    # class Meta:
    #     model = User
    #     # These fields are your User model's fields
    #     # fields = ('username', 'email', 'first_name', 'last_name')
    #     fields = ["username", "email", "password1", "password2"]


    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nav_context'] = {'user_info' : 'active'}
        return context



def address_view(request):

    if  not(request.user.is_authenticated):
        stuff_for_frontend = {
            'valid_search_str': False,
            'search_str': 'You have no permission to view this profile.',
        }

        return render(request, 'myApp/search.html', stuff_for_frontend)


    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AddressForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            try:
                with transaction.atomic():
                    address = Address.objects.filter(user=request.user.id).first()

                    address.address_str = form.cleaned_data['address_str']
                    address.number = form.cleaned_data['number']
                    address.street = form.cleaned_data['street']
                    address.sub_district  = form.cleaned_data['sub_district']
                    address.district = form.cleaned_data['district']
                    address.province = form.cleaned_data['province']
                    address.postal_code = form.cleaned_data['postal_code']

                    address.save()

            except IntegrityError:
                return redirect_to_home_something_went_wrong(request)
            return HttpResponseRedirect('/home')

        # if a GET (or any other method) we'll create a blank form
    else:

        if not(Address.objects.filter(user=request.user.id).exists()):
            try:
                with transaction.atomic():
                    address = Address.objects.create(user=request.user)
                    address.save()
            except IntegrityError:
                return redirect_to_home_something_went_wrong(request)

        address = Address.objects.filter(user=request.user.id).first()

        initial = {
            'address_str': address.address_str,
            'number': address.number,
            'street' : address.street,
            'sub_district' : address.sub_district,
            'district' : address.district,
            'province' : address.province,
            'postal_code' : address.postal_code,}

        form = AddressForm(initial=initial)

    stuff_for_frontend = {
        'form' : form,
        'nav_context' : { 'address' : 'active'},
    }
    return render(request, 'registration/address.html', stuff_for_frontend)
