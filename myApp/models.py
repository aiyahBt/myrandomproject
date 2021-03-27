from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


class Search(models.Model):
    search = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.search)

    class Meta:
        verbose_name_plural = 'Searches'


class Book(models.Model):
    isbn_13 = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100, null=True)
    author = models.CharField(max_length=100, null=True)
    publish_date = models.CharField(max_length=100,
                                    null=True)  # It says date but actually return just year from a json file.
    publishers = models.CharField(max_length=100, null=True)  # Not good, but need to get it done quickly.
    isbn_10 = models.CharField(max_length=20, null=True)
    img_url = models.CharField(max_length=200, null=True)

    owned_by = models.ManyToManyField(User, through='User_Book')

    def __str__(self):
        return '{}, {}, {}'.format(self.title, self.author, self.isbn_13)


class Cached_Book(models.Model):  # Every time user searches, we will update the information to this DB.
    isbn_13 = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100, null=True)
    author = models.CharField(max_length=100, null=True)
    publish_date = models.CharField(max_length=100,
                                    null=True)  # It says date but actually return just year from a json file.
    publishers = models.CharField(max_length=100, null=True)  # Not good, but need to get it done quickly.
    isbn_10 = models.CharField(max_length=20, null=True)
    img_url = models.CharField(max_length=200, null=True)

    on_wishlist = models.ManyToManyField(User, through='Wish_List')

    def __str__(self):
        return '{}, {}, {}'.format(self.title, self.author, self.isbn_13)


class User_Book(models.Model):  # Owner of the book.
    bookID = models.AutoField(primary_key=True)  # Ownership
    userID = models.ForeignKey(User, on_delete=models.CASCADE)  # user.id
    isbn_13 = models.ForeignKey(Book, on_delete=models.CASCADE)

    available = models.BooleanField(default=True)

    def __str__(self):
        str_available = ''
        if (self.available):
            str_available = 'available'
        return '{}, {}, {}, {}'.format(self.bookID, self.userID, self.isbn_13, str_available)


class Wish_List(models.Model):
    userID = models.ForeignKey(User, on_delete=models.CASCADE)  # user.id
    isbn_13 = models.ForeignKey(Cached_Book, on_delete=models.CASCADE)

    def __str__(self):
        return '{}, {}, {}'.format(self.id, self.userID, self.isbn_13)


class Request(models.Model):  # User_2 have to select a book from user 1. Then, the request is transfered to Status.
    user_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='request_user_1')
    user_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='request_user_2')

    book_1 = models.ForeignKey(User_Book, on_delete=models.CASCADE, null=True, related_name='request_book_1')
    # User_2's Book which user_1 wants to read.
    book_2 = models.ForeignKey(User_Book, on_delete=models.CASCADE, null=False, related_name='request_book_2')

    denied = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        user_1_name = self.user_1.username
        user_2_name = self.user_2.username
        book_2_name = self.book_2.isbn_13.title

        return '{}, {}, {}, {}, denied:{},accepted:{}'.format(self.id, user_1_name, user_2_name, book_2_name,
                                                              self.denied, self.accepted)


class Status(models.Model):  # After the request is accepted by user2.
    # User who forms a request.
    user_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='status_user_1')
    # user who is to accept.
    user_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='status_user_2')

    # User's 1 book.
    book_1 = models.ForeignKey(User_Book, on_delete=models.CASCADE, related_name='status_book_1')
    # User's 2 book.
    book_2 = models.ForeignKey(User_Book, on_delete=models.CASCADE, related_name='status_book_2')


    preparing_my_book = 'pp'
    my_book_is_sent = 'ms'
    your_book_is_sent = 'ys'
    complete = 'cp'
    user_status_choices = [
        (preparing_my_book, 'Preparing my book.'),
        (my_book_is_sent, 'My book is sent.'),
        (your_book_is_sent, 'Your book is sent back.'),
        (complete, 'Complete'),  # When you receive your own book.
    ]

    user_1_status = models.CharField(max_length=2, choices=user_status_choices)

    user_2_status = models.CharField(max_length=2, choices=user_status_choices)

    # If both books are sent back to the owners, exchange_status will be completed.
    # Set both books to active.
    exchange_active = models.BooleanField(default=True)

    def __str__(self):
        user_1_name = self.user_1.username
        user_2_name = self.user_2.username
        book_1_title = self.book_1.isbn_13.title
        book_2_title = self.book_2.isbn_13.title

        return '{}, {}, {}, {}, {}, user_1:{}, user_2:{}'.format(self.id, user_1_name, user_2_name,
                                                                book_1_title, book_2_title,
                                                                self.user_1_status, self.user_2_status)

    def get_status_string(self, user_n):

        if (user_n == 1):
            string =  self.user_1_status
        elif(user_n == 2):
            string = self.user_2_status
        else:
            return 'invalid'

        for e in self.user_status_choices:
            if e[0] == string:
                return e[1]


