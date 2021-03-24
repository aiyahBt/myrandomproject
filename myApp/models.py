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
    publish_date = models.CharField(max_length=100, null=True)  # It says date but actually return just year from a json file.
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
        return '{}, {}, {}'.format(self.bookID, self.userID, self.isbn_13)


class Wish_List(models.Model):
    userID = models.ForeignKey(User, on_delete=models.CASCADE)  # user.id
    isbn_13 = models.ForeignKey(Cached_Book, on_delete=models.CASCADE)

    def __str__(self):
        return '{}, {}, {}'.format(self.id, self.userID, self.isbn_13)


class Request(models.Model):  # User_2 have to select a book from user 1. Then, the request is transfered to Status.
    user_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='request_user_1')
    user_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='request_user_2')

    # User_2's Book which user_1 wants to read.
    book_2 = models.ForeignKey(Book, on_delete=models.CASCADE)

    canceled = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        user_1_name = User.objects.get(pk=self.user_1.pk).username
        user_2_name = User.objects.get(pk=self.user_2.pk).username
        book_2_name = Book.objects.get(pk=self.book_2.pk).title

        return '{}, {}, {}, {}'.format(self.id,  user_1_name, user_2_name, book_2_name)

class Status(models.Model):  # After the request is accepted by user2.
    # User who forms a request.
    user_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='status_user_1')
    # user who is to accept.
    user_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='status_user_2')

    # User's 1 book.
    book_1 = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='status_book_1')
    # User's 2 book.
    book_2 = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='status_book_2')

    user_status_choices = [
        ('pp', 'Preparing my book.'),
        ('ms', 'My book is sent.'),
        ('ys', 'Your book is sent back.'),
        ('cp', 'Complete'),  # When you receive your own book.
    ]

    user_1_status = models.CharField(max_length=2, choices=user_status_choices)

    user_2_status = models.CharField(max_length=2, choices=user_status_choices)

    # If both books are sent back to the owners, exchange_status will be completed.
    # Set both books to active.
    exchange_active = models.BooleanField(default=True)
