from django.contrib import admin

# Register your models here.
from .models import Address
from . import forms
from django.contrib.auth.models import User

#admin.site.register(User)


admin.site.register(Address)

