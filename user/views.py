from django.shortcuts import render
import requests
from requests.compat import quote_plus
from myApp import models as myApp_models


def shelf_view(request):
    user = request.user

    query_set = myApp_models.User_Book.objects.filter(userID=user.id)
    isbn_list = query_set.values_list('isbn_13', flat=True)

    book_list = list( myApp_models.Book.objects.filter(isbn_13__in=isbn_list) )

    stuff_for_frontend = {
        'book_list' : book_list
    }
    return render(request, 'user/shelf.html', stuff_for_frontend)

def wish_list_view(request):
    user = request.user

    query_set = myApp_models.Wish_List.objects.filter(userID=user.id)
    isbn_list = query_set.values_list('isbn_13', flat=True)

    book_list = list( myApp_models.Cached_Book.objects.filter(isbn_13__in=isbn_list) )

    stuff_for_frontend = {
        'book_list' : book_list
    }
    return render(request, 'user/shelf.html', stuff_for_frontend)