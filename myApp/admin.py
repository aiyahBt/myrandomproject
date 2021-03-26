from django.contrib import admin
from .models import Book, Cached_Book, User_Book, Wish_List, Request, Status
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db import models

from django.contrib import admin

# class customUserView(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#
#
# class UserInline(admin.StackedInline):
#     model = customUserView
#
#     can_delete = False
#
# # Define a new User admin
# class UserAdmin(BaseUserAdmin):
#     inlines = (UserInline, )
#
# # Re-register UserAdmin
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)


admin.site.register(Cached_Book)
admin.site.register(Book)
admin.site.register(User_Book)
admin.site.register(Wish_List)
admin.site.register(Request)
# admin.site.register(Status)


class Status_admin_view(admin.ModelAdmin):
    # readonly_fields  = ('user_1', 'user_2', 'book_1', 'book_2', 'user_1_status', 'user_2_status',) # Enter full list of fields here
    readonly_fields  = ('user_1_status', 'user_2_status',) # Enter full list of fields here


admin.site.register(Status)
