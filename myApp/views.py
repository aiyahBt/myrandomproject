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
        # 'user': user,
    }

    return render(request, 'home.html', stuff_for_frontend)


BASE_ISBN_URL = 'https://openlibrary.org/isbn/{}.json'
BASE_IMAGE_URL = 'https://covers.openlibrary.org/b/isbn/{}-M.jpg'
INFO_URL = 'https://openlibrary.org/isbn/{}'


def search_isbn(request):

    search_str = request.POST.get('search')
    search_option = request.POST.get('cat')

    stuff_for_frontend = {
        'valid_search_str': False,
        'search_str': 'Invalid search string.',
    }

    if not(search_str): #If none/null/empty
        return render(request, 'myApp/search.html', stuff_for_frontend)

    #search_str = isbnlib.clean(search_str)
    if not(isbnlib.is_isbn10(search_str) or isbnlib.is_isbn13(search_str)):
        return render(request, 'myApp/search.html', stuff_for_frontend)

    search_str = isbnlib.to_isbn13(search_str) #transform to isbn 13.
    search_str = isbnlib.canonical(search_str) #remove hyphen (Dash, -).

    #check if is in Cached_Book.
    isbn_13_int = int(search_str)

    books = models.Cached_Book.objects.filter(isbn_13 = isbn_13_int)
    book = models.Cached_Book(isbn_13=isbn_13_int)

    book.isbn_13 = isbn_13_int

    #books.exists()
    if (books.exists()):
        book = books.first()
    else:                    # Web scrapping process.

        detail_url = BASE_ISBN_URL.format(quote_plus(search_str))
        response = requests.get(detail_url)
        data = response.text

        if not(data):
            stuff_for_frontend['valid_search_str'] = False
            stuff_for_frontend['search_str'] = 'No data.'
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
        if (author) : #if(valid)
            author = author.get_text()
        else:
            author = ''
        title = details.get('title')
        publishers = ','.join(details.get('publishers'))  # transform to "abc,def
        publish_date = details.get('publish_date')
        if not(publish_date):
            publishers = ''

        img_url = BASE_IMAGE_URL.format(search_str)

        #Assign values to book.
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

    #sent stuff to front-end.
    book_details = {
        'title': book.title,
        'author': book.author,
        'publish_date': book.publish_date,
        'publishers': book.publishers,
    }

    stuff_for_frontend = {
        'valid_search_str' : True,
        'search_str': search_str,
        'book_details': book_details,
        'img_url': book.img_url,
    }

    return render(request, 'myApp/search.html', stuff_for_frontend)


def search(request):

    search_mode = 'isbn'

    if search_mode == 'isbn':
        return search_isbn(request)
    else:
        return
