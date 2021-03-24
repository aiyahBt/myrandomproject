from django.shortcuts import render
import requests
from requests.compat import quote_plus
from myApp import models as myApp_models
from django.contrib.auth.models import User


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

def request_exchange(request, isbn_13):
    in_isbn_13 = isbn_13

    #We know that the book exists.
    #book_query = myApp_models.Book.objects.filter(isbn_13=in_isbn_13)


    shelf_query = myApp_models.User_Book.objects.filter(userID=request.user.id)
    shelf_isbn_list = shelf_query.values_list('isbn_13', flat=True)

    user_book_query = myApp_models.User_Book.objects.filter(isbn_13=in_isbn_13)
    users_own_this_book = user_book_query.values_list('userID', flat=True)


    user_book = myApp_models.Wish_List.objects.filter(userID__in=users_own_this_book).filter( isbn_13__in=shelf_isbn_list).first() #Limit = 1

    user_2_obj = user_book.userID
    book = myApp_models.Book.objects.filter(isbn_13 = in_isbn_13).first()

    req = myApp_models.Request.objects.create(user_1 = request.user, user_2=user_2_obj, book_2=book)
    req.save()

    stuff_for_frontend = {
        'valid_search_str': False,
        'search_str': 'Request formed.',
    }

    return render(request, 'myApp/search.html', stuff_for_frontend)
