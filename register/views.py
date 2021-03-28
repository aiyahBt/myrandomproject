from django.shortcuts import render

# Create your views here.
# views.py
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.views import generic
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.urls import reverse_lazy
from django.contrib.auth.models import User


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
