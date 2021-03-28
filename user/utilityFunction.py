from myApp import models as myApp_models
from django.shortcuts import render

def validate_matching(request, bookID):

    user_book = myApp_models.User_Book.objects.get(pk=bookID)

    shelf_query = myApp_models.User_Book.objects.filter(userID=request.user.id)
    shelf_isbn_list = shelf_query.values_list('isbn_13')

    book_matching_query = myApp_models.Wish_List.objects.filter(userID=user_book.userID.pk,
                                                                isbn_13__in=shelf_isbn_list)

    return book_matching_query.exists()


def redirect_to_home_something_went_wrong(request):
    stuff_for_frontend = {
        'valid_search_str' : False,
        'search_str' : 'Something went wrong.'
    }

    return render(request, 'myApp/search.html', stuff_for_frontend)

