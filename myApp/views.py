import requests
from requests.compat import quote_plus
from django.shortcuts import render
from bs4 import BeautifulSoup
from django.contrib.auth import logout
from . import models
import json
import isbnlib


# Create your views here.
def home(request):
    stuff_for_frontend = {
        'nav_context' : {'home' : 'active'}
    }

    return render(request, 'home.html', stuff_for_frontend)


BASE_ISBN_URL = 'https://openlibrary.org/isbn/{}.json'
BASE_IMAGE_URL = 'https://covers.openlibrary.org/b/isbn/{}-M.jpg'
INFO_URL = 'https://openlibrary.org/isbn/{}'

def search_isbn_matching(request, isbn_13_int):

    stuff_for_frontend = {
        'valid_search_str': True,
        'search_str': isbn_13_int,
        'is_matched' : False,
        'user_book' : ''
    }

    user_book_query = models.User_Book.objects.filter(isbn_13 = isbn_13_int)
    shelf_query = models.User_Book.objects.filter(userID = request.user.id)

    if (shelf_query.filter(isbn_13=isbn_13_int).exists()):
        stuff_for_frontend['valid_search_str'] = False
        stuff_for_frontend['search_str'] = 'You own this book.'
    elif (user_book_query.exists()):

        #list of userID that own this book.
        # userID_query = user_book_query.values_list('userID')
        #
        # wish_list_isbn_list = models.Wish_List.objects.filter(userID__in=userID_query).values_list('isbn_13', flat=True).distinct()
        # shelf_isbn_list = models.User_Book.objects.filter(userID = request.user.id).values_list('isbn_13', flat=True)

        # In the future we might own multiple books of one isbn.
        shelf_isbn_list = shelf_query.values_list('isbn_13', flat=True).distinct()
        users_own_this_book = user_book_query.values_list('userID', flat=True)

        user_matched_from_wish_list = models.Wish_List.objects.filter(userID__in=users_own_this_book).\
            filter(isbn_13__in=shelf_isbn_list)

        if not(user_matched_from_wish_list.exists()):
            stuff_for_frontend['valid_search_str'] = False
            stuff_for_frontend['search_str'] = 'No matching book.'
            return render(request, 'myApp/search.html', stuff_for_frontend)


        book_matched = user_book_query.filter(userID=user_matched_from_wish_list.filter().userID.pk)


        if book_matched.exists(): #If intersection is not an empty set.
            stuff_for_frontend['book'] = book_matched.first().isbn_13  #send book object.
            stuff_for_frontend['is_matched'] = True
            stuff_for_frontend['user_book'] = book_matched.first()      #send the user_book object.
            print(stuff_for_frontend['book'])
            print(stuff_for_frontend['user_book'])

        else:
            stuff_for_frontend['valid_search_str'] = False
            stuff_for_frontend['search_str'] = 'No matching book.'

    else:
        stuff_for_frontend['valid_search_str'] = False
        stuff_for_frontend['search_str'] = 'No matching book.'

    return render(request, 'myApp/search.html', stuff_for_frontend)


def search_isbn(request):
    search_str = request.POST.get('search')
    search_option = request.POST.get('cat')


    if not (search_str):  # If none/null/empty

        stuff_for_frontend = {
            'valid_search_str': False,
            'search_str': 'Invalid search string.',
        }
        return render(request, 'myApp/search.html', stuff_for_frontend)

    # search_str = isbnlib.clean(search_str)
    if not (isbnlib.is_isbn10(search_str) or isbnlib.is_isbn13(search_str)):

        stuff_for_frontend = {
            'valid_search_str': False,
            'search_str': 'Invalid search string.',
        }
        return render(request, 'myApp/search.html', stuff_for_frontend)

    #Transform the string to isbn13-integer.
    search_str = isbnlib.to_isbn13(search_str)  # transform to isbn 13.
    search_str = isbnlib.canonical(search_str)  # remove hyphen (Dash, -).
    isbn_13_int = int(search_str)


    if (search_option == '1'):    #Search within database. (search in Book table.)
        book_query = models.Book.objects.filter(isbn_13=isbn_13_int)

        stuff_for_frontend = {
            'valid_search_str': True,
            'search_str': search_str,

        }
        if (book_query.exists()):
            stuff_for_frontend['book'] = book_query.first()
        else:
            stuff_for_frontend['valid_search_str'] = False
            stuff_for_frontend['search_str'] = 'This book is not available.'

        return render(request, 'myApp/search.html', stuff_for_frontend)

    elif (search_option == '2'): #Mathcing
        return search_isbn_matching(request, isbn_13_int)
    else: #seach_option == '0' (search from open library).
        book_query = models.Cached_Book.objects.filter(isbn_13=isbn_13_int)
        book = ''

        # check if is in Cached_Book.
        if (book_query.exists()):
            book = book_query.first()

            stuff_for_frontend = {
                'valid_search_str': True,
                'search_str': isbn_13_int,
                'book' : book,
            }

            return render(request, 'myApp/search.html', stuff_for_frontend)
        else:  # Web scrapping process.

            book = models.Cached_Book.objects.create(isbn_13=isbn_13_int)

            detail_url = BASE_ISBN_URL.format(quote_plus(search_str))
            response = requests.get(detail_url)
            data = response.text

            if not (data):
                stuff_for_frontend = {
                    'valid_search_str' : False,
                    'search_str' : 'No data.'
                }

                return render(request, 'myApp/search.html', stuff_for_frontend)

            # soup_1 to get detail
            soup = BeautifulSoup(data, features='html.parser')
            start = data.find('{')
            end = data.rfind('}')
            details = json.loads(data[start:end + 1])

            # soup_2 to get author
            info_url = INFO_URL.format(quote_plus(search_str))
            response = requests.get(info_url)
            data = response.text
            soup = BeautifulSoup(data, features='html.parser')
            author = soup.find("a", {"itemprop": "author"})
            if (author):  # if(valid)
                author = author.get_text()
            else:
                author = ''
            title = details.get('title')

            publishers = details.get('publishers')
            if (publishers):
                publishers = ','.join(details.get('publishers'))
            else:
                publishers = ''

            publish_date = details.get('publish_date')
            if not (publish_date):
                publishers = ''

            img_url = BASE_IMAGE_URL.format(search_str)

            # Assign values to book.
            book.isbn_13 = isbn_13_int
            book.title = title
            book.author = author
            book.publish_date = publish_date
            book.publishers = publishers

            book.img_url = img_url

            if len(search_str) == 10:
                book.isbn_10 = int(search_str)
            else:
                book.isbn_10 = None

            book.save()

            stuff_for_frontend = {
                'valid_search_str': True,
                'search_str': search_str,
                'book': book,
            }

            return render(request, 'myApp/search.html', stuff_for_frontend)


def search(request):
    search_by = 'isbn'

    if search_by == 'isbn':
        return search_isbn(request)
    else:
        return


def add_to_shelf(request, isbn_13=1234):

    in_isbn_13 = isbn_13

    book_query = models.Book.objects.filter(isbn_13=in_isbn_13)
    book = {}
    if (book_query.exists()):  # if does not exist, add it to Book.
        book = book_query.first()
    else:
        cached_book = models.Cached_Book.objects.filter(isbn_13=in_isbn_13).first()
        book = models.Book.objects.create(isbn_13=in_isbn_13)
        # book.__dict__.update(cached_book.__dict__) #Copy by hand .

        book.isbn_13 = cached_book.isbn_13
        book.title = cached_book.title
        book.author = cached_book.author
        book.publish_date = cached_book.publish_date
        book.publishers = cached_book.publishers
        book.isbn_10 = cached_book.isbn_10
        book.img_url = cached_book.img_url
        book.save()

    stuff_for_frontend={}
    #For now, we allow each user to own one copy of a book.
    if models.User_Book.objects.filter(userID=request.user.id, isbn_13=in_isbn_13).exists():
        stuff_for_frontend = { 'valid_search_str': False, 'search_str': 'You have this book!!!'}

    else:
        b = models.User_Book(userID=request.user, isbn_13=book)
        b.save()
        stuff_for_frontend = { 'valid_search_str': False, 'search_str': 'Added to shelf.'}

    return render(request, 'myApp/search.html', stuff_for_frontend)


def add_to_wish_list(request, isbn_13=1234):
    stuff_for_frontend = {
        'valid_search_str': False,
        'search_str': 'Added to shelf.',
    }
    in_isbn_13 = isbn_13

    cached_book_query = models.Cached_Book.objects.filter(isbn_13=in_isbn_13)
    book = cached_book_query.first()
    if request.user.id in cached_book_query.first().on_wishlist.all().values_list('id', flat=True):
        stuff_for_frontend['search_str'] = 'Already on wish list.'
        return render(request, 'myApp/search.html', stuff_for_frontend)

    book_query = models.Book.objects.filter(isbn_13=in_isbn_13)

    if book_query.exists() and request.user.id in book_query.first().owned_by.all().values_list('id', flat=True):
        stuff_for_frontend['search_str'] = 'You have this book!!!'
    else:
        b = models.Wish_List(userID=request.user, isbn_13=book)
        b.save()
        stuff_for_frontend['search_str'] = 'Added to wish list.'

    return render(request, 'myApp/search.html', stuff_for_frontend)
