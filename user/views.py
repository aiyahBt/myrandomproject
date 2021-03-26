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
        'book_list'   : book_list,
        'nav_context' :  { 'shelf':'active'},

    }
    return render(request, 'user/shelf.html', stuff_for_frontend)

def wish_list_view(request):
    user = request.user

    query_set = myApp_models.Wish_List.objects.filter(userID=user.id)
    isbn_list = query_set.values_list('isbn_13', flat=True)

    book_list = list( myApp_models.Cached_Book.objects.filter(isbn_13__in=isbn_list) )

    stuff_for_frontend = {
        'book_list' : book_list,
        'nav_context': {'wish_list': 'active'},

    }
    return render(request, 'user/shelf.html', stuff_for_frontend)

# from user.views import in_request_view
def in_request_view(request):
    #user = User.objects.get(username='Tata')
    user_id = request.user.id

    in_requests_list = list(myApp_models.Request.objects.filter(user_2 = user_id, denied=False, accepted=False)) # Pick ones that are active.


    request_list_to_frontend = []
    for e in in_requests_list:
        temp_obj = {
            'id' : e.id,  #request id
            'user' : e.user_1,
            'book' : e.book_2,
        }
        request_list_to_frontend.append(temp_obj)


    stuff_for_frontend = {
        'request_list_to_frontend': request_list_to_frontend,
        'nav_context': {'in_request': 'active'},

    }

    #return in_requests_list

    return render(request, 'user/in_request.html', stuff_for_frontend)

def request_detail_view(request, request_id , book_1_isbn_13, denied , accepted ):
    denied = bool(denied)
    accepted = bool(accepted)
    print(denied)
    print(accepted)
    stuff_for_frontend = {

    }

    in_request = myApp_models.Request.objects.get(id=request_id)
    if in_request.user_2.id != request.user.id:
        print()
        #You have no permission to access this request.


    stuff_for_frontend = {
        'nav_context': {'in_request': 'active'},

    }

    if (denied):
        in_request.denied = True
        in_request.save()
        print()

        return render(request, 'user/in_request.html', stuff_for_frontend)

    elif (accepted):

        in_request.accepted = True
        in_request.save()

        book_1 = myApp_models.User_Book.objects.filter(userID = in_request.user_1.pk, isbn_13=book_1_isbn_13).first() #The selected book that request.user wants to read, it is user_1's book.

        #Update and save.
        other_in_requests = myApp_models.Request.objects.filter(user_2=request.user.id, book_2=in_request.book_2.pk).\
            exclude(accepted = True)
        other_in_requests.update(denied=True)

        for e in other_in_requests:
            e.save()

        #Set both book to not Available.
        # print(in_request.user_1.pk)
        # print(in_request.book_2.pk)
        book_2 = myApp_models.User_Book.objects.filter(userID = request.user.id, isbn_13=in_request.book_2.pk).first()

        book_2.available = False
        book_1.available = False
        book_1.save()
        book_2.save()



        status_obj = myApp_models.Status.objects.create(user_1 = in_request.user_1, user_2 = request.user,
                                           book_1 = book_1, book_2 = book_2,
                                           user_1_status = 'pp', user_2_status='pp')
        status_obj.save()

        return render(request, 'user/in_request.html', stuff_for_frontend)

    else:
        user_wish_list = myApp_models.Wish_List.objects.filter(userID=request.user.id)
        user_isbn_13_list = user_wish_list.values_list('isbn_13', flat=True)

        book_from_requesting_user = myApp_models.User_Book.objects.filter(userID=in_request.user_1, available=True, isbn_13__in=user_isbn_13_list )

        book_list = []
        for e in book_from_requesting_user:
            book_list.append( e.isbn_13)

            print(e.isbn_13)

        stuff_for_frontend['request_id'] = request_id
        stuff_for_frontend['book_list'] = book_list

    return render(request, 'user/request_detail.html', stuff_for_frontend)
        #render request_detail_view


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

def active_exchange_view(request):

    status_as_user_1_query = myApp_models.Status.objects.filter(user_1 = request.user.id, exchange_active = True)
    status_as_user_2_query = myApp_models.Status.objects.filter(user_2 = request.user.id, exchange_active = True)

    status_class = myApp_models.Status
    status_list = []

    for e in status_as_user_1_query:
        temp_obj = {
            'id' : e.id,
            'involving_user' : e.user_2,
            'your_book' : e.book_1.isbn_13,
            'involving_user_book' : e.book_2.isbn_13,
            'your_status': e.get_status_string(1),
            'involving_user_status': e.get_status_string(2),
        }
        status_list.append(temp_obj)

    for e in status_as_user_2_query:
        temp_obj = {
            'id' : e.id,
            'involving_user' : e.user_1,
            'your_book' : e.book_2.isbn_13,
            'involving_user_book' : e.book_1.isbn_13,
            'your_status' : e.get_status_string(2),
            'involving_user_status' : e.get_status_string(1),
        }
        status_list.append(temp_obj)

    stuff_for_frontend = {
        'status_list' : status_list,
        'nav_context': {'active_exchange': 'active'},
    }
    return render(request, 'user/active_exchange.html', stuff_for_frontend)

def exchange_detail_view(request, id):

    status = myApp_models.Status.objects.get(id=id)
    is_user_1 = (User.objects.get(pk=request.user.id).id == status.user_1.id)

    stuff_for_frontend = {
        'status': status,
        'nav_context': {'status_detail': 'active'},
        'is_user_1' : is_user_1,
    }

    return render(request, 'user/exchange_detail.html', stuff_for_frontend)









