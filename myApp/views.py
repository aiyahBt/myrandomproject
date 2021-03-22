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
    # need to check validity of isbn 10  13 digits
    search_str = request.POST.get('search')

    stuff_for_frontend = {
        'valid_search_str': False,
        'search_str': 'Invalid search string.',
    }

    if not(search_str): #If none/null/empty
        return render(request, 'myApp/search.html', stuff_for_frontend)

    #search_str = isbnlib.clean(search_str)
    if not(isbnlib.is_isbn10(search_str) or isbnlib.is_isbn13(search_str)):
        return render(request, 'myApp/search.html', stuff_for_frontend)

    #Everything is valid.

    detail_url = BASE_ISBN_URL.format(quote_plus(search_str))
    response = requests.get(detail_url)
    data = response.text

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
    author = soup.find("a", {"itemprop": "author"}).get_text()

    title = details.get('title')
    publishers = ','.join(details.get('publishers'))  # transform to "abc,def
    publish_date = details.get('publish_date')

    img_url = BASE_IMAGE_URL.format(search_str)

    book_details = {
        'title': title,
        'author': author,
        'publish_date': publish_date,
        'publishers': publishers,
    }

    stuff_for_frontend = {
        'valid_search_str' : True,
        'search_str': search_str,
        'book_details': book_details,
        'img_url': img_url,
    }

    return render(request, 'myApp/search.html', stuff_for_frontend)


def search(request):
    search_str = request.POST.get('search')
    # print(search_str)
    stuff_for_frontend = {
        'search_str': search_str,
    }
    return render(request, 'myApp/search.html', stuff_for_frontend)

