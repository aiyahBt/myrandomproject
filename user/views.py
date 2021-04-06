from django.shortcuts import render, redirect
import requests
from requests.compat import quote_plus
from myApp import models as myApp_models
from django.contrib.auth.models import User
from django import forms
from .utilityFunction import validate_matching, redirect_to_home_something_went_wrong
from django.db import IntegrityError, transaction
from register.models import Address


def shelf_view(request):
    user = request.user

    query_set = myApp_models.User_Book.objects.filter(userID=user.id, available=True)
    isbn_list = query_set.values_list('isbn_13', flat=True)

    book_list = list(myApp_models.Book.objects.filter(isbn_13__in=isbn_list))

    stuff_for_frontend = {
        'book_list': book_list,
        'nav_context': {'shelf': 'active'},

    }
    return render(request, 'user/shelf.html', stuff_for_frontend)


def wish_list_view(request):
    user = request.user

    query_set = myApp_models.Wish_List.objects.filter(userID=user.id)
    isbn_list = query_set.values_list('isbn_13', flat=True)

    book_list = list(myApp_models.Cached_Book.objects.filter(isbn_13__in=isbn_list))

    stuff_for_frontend = {
        'book_list': book_list,
        'nav_context': {'wish_list': 'active'},

    }
    return render(request, 'user/shelf.html', stuff_for_frontend)


# from user.views import in_request_view
def in_request_view(request):
    in_requests_list = myApp_models.Request.objects.filter(user_2=request.user.id,
                                                           denied=False,
                                                           accepted=False)  # Pick ones that are active.

    this_user_wish_list_query = myApp_models.Wish_List.objects.filter(userID=request.user.id). \
        values_list('isbn_13', flat=True)

    for req in in_requests_list:
        user_1_shelf_query = myApp_models.User_Book.objects.filter(userID=req.user_1.pk,
                                                                   isbn_13__in=this_user_wish_list_query,
                                                                   available=True)
        if not (user_1_shelf_query.exists()):
            req.denied = True
            req.save()

    in_requests_list = myApp_models.Request.objects.filter(user_2=request.user.id,
                                                           denied=False,
                                                           accepted=False)  # Pick ones that are active.

    stuff_for_frontend = {
        'in_requests_list': in_requests_list,
        'nav_context': {'in_request': 'active'},

    }

    return render(request, 'user/in_request.html', stuff_for_frontend)


def out_request_view(request):
    user_id = request.user.id

    out_request_list = myApp_models.Request.objects.filter(user_1=user_id, denied=False, accepted=False)

    stuff_for_frontend = {
        'out_request_list': out_request_list,
        'nav_context': {'out_request': 'active'},

    }

    return render(request, 'user/out_request.html', stuff_for_frontend)


# This code is so bad, I tried to bundle functionality within one function.
def request_detail_view(request, request_id, book_1_isbn_13, denied, accepted):
    denied = bool(denied)
    accepted = bool(accepted)

    stuff_for_frontend = {
    }

    # Assume that only user_2 can deny or accept the request.
    in_request = myApp_models.Request.objects.get(pk=request_id)

    if not (in_request):
        stuff_for_frontend = {
            'valid_search_str': False,
            'search_str': 'Such request does not exits.',
        }
        return render(request, 'myApp/search.html', stuff_for_frontend)

    if (in_request.denied or in_request.accepted):
        stuff_for_frontend = {
            'valid_search_str': False,
            'search_str': 'You cannot make changes the request.',
        }
        return render(request, 'myApp/search.html', stuff_for_frontend)

    # Allow only user 2 to make changes to request.
    if in_request.user_2.id != request.user.id:
        stuff_for_frontend = {
            'valid_search_str': False,
            'search_str': 'You have no permission to access this request.',
        }
        return render(request, 'myApp/search.html', stuff_for_frontend)

    # print(in_request)
    stuff_for_frontend = {
        'nav_context': {'in_request': 'active'},
    }

    if (denied):
        try:
            with transaction.atomic():
                in_request.denied = True
                in_request.save()
        except IntegrityError:
            return redirect_to_home_something_went_wrong(request)

        return render(request, 'user/in_request.html', stuff_for_frontend)

    elif (accepted):

        try:
            with transaction.atomic():
                in_request.accepted = True
                in_request.save()

                # Delete wish list.
                user_1_wish_list_query = myApp_models.Wish_List.objects.filter(userID=in_request.user_1.id,
                                                                               isbn_13=in_request.book_2.isbn_13.pk)
                if (user_1_wish_list_query.exists()):
                    user_1_wish_list_query.delete()

                book_1 = myApp_models.User_Book.objects.filter(userID=in_request.user_1.pk,
                                                               isbn_13=book_1_isbn_13).first()  # The selected book that request.user wants to read, it is user_1's book.

                # Update and save.
                other_in_requests = myApp_models.Request.objects.filter(user_2=request.user.id,
                                                                        book_2=in_request.book_2.pk). \
                    exclude(accepted=True)

                other_in_requests.update(denied=True)

                for e in other_in_requests:
                    e.save()

                book_2 = in_request.book_2

                book_2.available = False
                book_1.available = False
                book_1.save()
                book_2.save()

                status_obj = myApp_models.Status.objects.create(user_1=in_request.user_1, user_2=request.user,
                                                                book_1=book_1, book_2=book_2,
                                                                user_1_status='pp', user_2_status='pp')
                status_obj.save()
        except IntegrityError:
            return redirect_to_home_something_went_wrong(request)

        # return render(request, 'user/in_request.html', stuff_for_frontend)
        #return redirect('user/in_request/')
        return in_request_view(request)

    else:  # accepted = False and denied = False [Just want to view the request.]
        user_wish_list = myApp_models.Wish_List.objects.filter(userID=request.user.id)
        user_isbn_13_list = user_wish_list.values_list('isbn_13', flat=True)

        book_from_requesting_user = myApp_models.User_Book.objects.filter(userID=in_request.user_1, available=True,
                                                                          isbn_13__in=user_isbn_13_list)

        book_list = []
        for e in book_from_requesting_user:
            book_list.append(e.isbn_13)

            # print(e.isbn_13)

        stuff_for_frontend['request_id'] = request_id
        stuff_for_frontend['book_list'] = book_list

    return render(request, 'user/request_detail.html', stuff_for_frontend)
    # render request_detail_view


def request_exchange(request, bookID):
    # Checking Validity by trying to do match checking.

    # validate matching to prevent user from playing with string.

    user_book_query = myApp_models.User_Book.objects.filter(pk=bookID)
    if not (user_book_query.exists()):
        stuff_for_frontend = {
            'valid_search_str': False,
            'search_str': 'This book does not exist. What are you talking about.',
        }

        return render(request, 'myApp/search.html', stuff_for_frontend)

    user_book = user_book_query.first()
    print(user_book)
    if not (validate_matching(request, bookID)):
        stuff_for_frontend = {
            'valid_search_str': False,
            'search_str': 'You cannot form this request.',
        }
        return render(request, 'myApp/search.html', stuff_for_frontend)

    # We allow only one out request per title.

    this_user_request_query = myApp_models.Request.objects.filter(user_1=request.user.id, accepted=False, denied=False)
    this_user_request_isbn_list = set([ e.book_2.isbn_13.isbn_13 for e in this_user_request_query])
    # print(this_user_request_query)
    # print(user_book.isbn_13.isbn_13 in this_user_request_isbn_list)
    if myApp_models.Request.objects.filter(book_2=bookID, user_1=request.user.id,
                                           accepted=False, denied=False).exists()  or user_book.isbn_13.isbn_13 in this_user_request_isbn_list :
        stuff_for_frontend = {
            'valid_search_str': False,
            'search_str': 'This title is already in your request.',
        }
        return render(request, 'myApp/search.html', stuff_for_frontend)

    # shelf_query = myApp_models.User_Book.objects.filter(userID=request.user.id)
    # shelf_isbn_list = shelf_query.values_list('isbn_13', flat=True)
    #
    # user_book_query = myApp_models.User_Book.objects.filter(isbn_13=in_isbn_13)
    # users_own_this_book = user_book_query.values_list('userID', flat=True)
    #
    # #The user who on the book we are searching, such that we have the books that are on their wish-lists. Pick just one.
    # user_book = myApp_models.Wish_List.objects.filter(userID__in=users_own_this_book).filter( isbn_13__in=shelf_isbn_list).first() #Limit = 1
    #
    # user_2_obj = user_book.userID
    # book = myApp_models.User_Book.objects.filter(isbn_13 = in_isbn_13, userID=user_2_obj.id).first() #In the future, we want to let people own more that on book of each ISBN-13.
    try:
        with transaction.atomic():
            req = myApp_models.Request.objects.create(user_1=request.user, user_2=user_book.userID, book_2=user_book)
            req.save()
    except IntegrityError:
        return redirect_to_home_something_went_wrong(request)

    stuff_for_frontend = {
        'valid_search_str': False,
        'search_str': 'Request formed.',
    }

    return render(request, 'myApp/search.html', stuff_for_frontend)


def active_exchange_view(request):
    status_as_user_1_query = myApp_models.Status.objects.filter(user_1=request.user.id, exchange_active=True)
    status_as_user_2_query = myApp_models.Status.objects.filter(user_2=request.user.id, exchange_active=True)

    # status_class = myApp_models.Status
    status_list = []

    for e in status_as_user_1_query:
        temp_obj = {
            'id': e.id,
            'involving_user': e.user_2,
            'your_book': e.book_1.isbn_13,
            'involving_user_book': e.book_2.isbn_13,
            'your_status': e.get_user_1_status_display(),
            'involving_user_status': e.get_user_2_status_display(),
        }
        status_list.append(temp_obj)

    for e in status_as_user_2_query:
        temp_obj = {
            'id': e.id,
            'involving_user': e.user_1,
            'your_book': e.book_2.isbn_13,
            'involving_user_book': e.book_1.isbn_13,
            'your_status': e.get_user_2_status_display(),
            'involving_user_status': e.get_user_1_status_display(),
        }
        status_list.append(temp_obj)

    stuff_for_frontend = {
        'status_list': status_list,
        'nav_context': {'active_exchange': 'active'},
    }
    return render(request, 'user/active_exchange.html', stuff_for_frontend)


def exchange_detail_view(request, id):
    status = myApp_models.Status.objects.get(pk=id)

    if request.user.id != status.user_1.id and request.user.id != status.user_2.id:  # No permisson.
        stuff_for_frontend = {
            'valid_search_str': False,
            'search_str': 'You have no permission to access this exchange.',
        }
        return render(request, 'myApp/search.html', stuff_for_frontend)

    # Do not allow user to set the new user_status value. -> render active exchange without
    if not (status.exchange_active):
        stuff_for_frontend = {
            'status': status,
            'nav_context': {'active_exchange': 'active'},
        }
        return render(request, 'user/active_exchange.html', stuff_for_frontend)

    if status.user_1_status == myApp_models.Status.complete and status.user_2_status == myApp_models.Status.complete:

        try:
            with transaction.atomic():
                status.exchange_active = False
                status.save()

                status.book_1.available = True
                status.book_2.available = True

                status.book_2.save()
                status.book_1.save()

        except IntegrityError:
            return redirect_to_home_something_went_wrong(request)

        return active_exchange_view(request)

    is_user_1 = (User.objects.get(pk=request.user.id).id == status.user_1.id)

    swapped_status = status

    if not (Address.objects.filter(user=status.user_1).exists()):
        try:
            with transaction.atomic():
                address = Address.objects.create(user=status.user_1)
                address.save()
        except IntegrityError:
            return redirect_to_home_something_went_wrong(request)
    if not (Address.objects.filter(user=status.user_2).exists()):
        try:
            with transaction.atomic():
                address = Address.objects.create(user=status.user_2)
                address.save()
        except IntegrityError:
            return redirect_to_home_something_went_wrong(request)

    # We will always send address_1 as this user's address.
    address_1 = Address.objects.filter(user=request.user.id).first()
    address_2 = ''
    if not (is_user_1):  # swap role
        swapped_status = myApp_models.Status(user_1=status.user_2, user_2=status.user_1,
                                             book_1=status.book_2, book_2=status.book_1,
                                             user_1_status=status.user_2_status, user_2_status=status.user_1_status)
        address_2 = Address.objects.filter(user=status.user_1).first()
    else:
        address_2 = Address.objects.filter(user=status.user_2).first()

    class status_form(forms.Form):
        status = forms.ChoiceField(choices=myApp_models.Status.user_status_choices)

    status_selection_form = status_form(initial={'status': swapped_status.user_1_status})

    # print(status_selection_form)
    Address.objects.filter(user=request.user.id)

    stuff_for_frontend = {
        'status': status,
        'nav_context': {'status_detail': 'active'},
        'status_selection_form': status_selection_form,
        'swapped_status': swapped_status,
        'address': [address_1, address_2],
    }

    return render(request, 'user/exchange_detail.html', stuff_for_frontend)


def set_exchange_status(request, status_id):
    status_choice = request.POST.get('status')

    status = myApp_models.Status.objects.get(pk=status_id)

    if not (status.exchange_active):  # render active exchange without letting user set the new value.
        stuff_for_frontend = {
            'status': status,
            'nav_context': {'active_exchange': 'active'},
        }
        return render(request, 'user/active_exchange.html', stuff_for_frontend)

    # print(status.user_1.id)
    if (request.user.id == status.user_1.id):
        status.user_1_status = status_choice
    elif (request.user.id == status.user_2.id):
        status.user_2_status = status_choice
    # No permission.
    else:
        stuff_for_frontend = {
            'valid_search_str': False,
            'search_str': 'You have no permission to access this exchange.',
        }

        return render(request, 'myApp/search.html', stuff_for_frontend)

    try:
        with transaction.atomic():
            status.save()
    except IntegrityError:
        return redirect_to_home_something_went_wrong(request)

    return exchange_detail_view(request, status_id)


def completed_exchange_view(request):
    status_as_user_1_query = myApp_models.Status.objects.filter(user_1=request.user.id, exchange_active=False)
    status_as_user_2_query = myApp_models.Status.objects.filter(user_2=request.user.id, exchange_active=False)

    status_list = []

    for e in status_as_user_1_query:
        temp_obj = {
            'id': e.id,
            'involving_user': e.user_2,
            'your_book': e.book_1.isbn_13,
            'involving_user_book': e.book_2.isbn_13,
            'your_status': e.get_user_1_status_display(),
            'involving_user_status': e.get_user_2_status_display(),
        }
        status_list.append(temp_obj)

    for e in status_as_user_2_query:
        temp_obj = {
            'id': e.id,
            'involving_user': e.user_1,
            'your_book': e.book_2.isbn_13,
            'involving_user_book': e.book_1.isbn_13,
            'your_status': e.get_user_2_status_display(),
            'involving_user_status': e.get_user_1_status_display(),
        }
        status_list.append(temp_obj)

    stuff_for_frontend = {
        'status_list': status_list,
        'nav_context': {'completed_exchange': 'active'},
    }
    return render(request, 'user/completed_exchange.html', stuff_for_frontend)


def user_profile_view(request, id):  # We will expand this view to other users in the near future.

    if (request.user.id == id):  # view your own profile.

        stuff_for_frontend = {

        }

        return render(request, 'user/profile.html', stuff_for_frontend)

    else:  # For now this is not permitted.

        stuff_for_frontend = {
            'valid_search_str': False,
            'search_str': 'You have no permission to view this profile.',
        }

        return render(request, 'myApp/search.html', stuff_for_frontend)


def user_info_view(request):
    if not (request.user.is_authenticated):
        stuff_for_frontend = {
            'valid_search_str': False,
            'search_str': 'You have no permission to view this profile.',
        }

        return render(request, 'myApp/search.html', stuff_for_frontend)

    return
