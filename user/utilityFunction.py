from myApp import models as myApp_models

def validate_matching(request, bookID):

    user_book = myApp_models.User_Book.objects.get(pk=bookID)

    shelf_query = myApp_models.User_Book.objects.filter(userID=request.user.id)
    shelf_isbn_list = shelf_query.values_list('isbn_13')

    book_matching_query = myApp_models.Wish_List.objects.filter(userID=user_book.userID.pk,
                                                                isbn_13__in=shelf_isbn_list)

    return book_matching_query.exists()