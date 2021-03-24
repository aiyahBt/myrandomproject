from django.contrib import admin
from .models import Book, Cached_Book, User_Book, Wish_List
# Register your models here.


admin.site.register(Cached_Book)
admin.site.register(Book)
admin.site.register(User_Book)
admin.site.register(Wish_List)
