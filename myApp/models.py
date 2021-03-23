from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

#DROP TABLE myApp_Cached_Book;
#DROP TABLE myApp_Book;

# Create your models here.
class Search(models.Model):
    search = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.search)

    class Meta:
        verbose_name_plural = 'Searches'


class Book(models.Model):
    isbn_13 = models.IntegerField(          primary_key=True)
    title = models.CharField(               max_length=100, null=True)
    author = models.CharField(              max_length=100, null=True)
    publish_date = models.IntegerField(                     null=True)           # It says date but actually return just year from a json file.
    publishers = models.CharField(          max_length=100, null=True)  # Not good, but need to get it done quickly.
    isbn_10 = models.IntegerField(                          null=True)
    img_url = models.CharField(             max_length=200, null=True)

    def __str__(self):
        return '{}, {}, {}'.format(self.title, self.author, self.isbn_13)

class Cached_Book(Book): #Every time user searches, we will update the information to this DB.
    pass


class User_Book(models.Model): #Owner of the book.
    BookID = models.AutoField(primary_key=True)
    userID = models.ForeignKey(User, on_delete=models.CASCADE)  # user.id
    isbn_13 = models.ForeignKey(Book, on_delete=models.CASCADE)


    def __str__(self):
        return '{}, {}, {}'.format(self.BookID, self.userID, self.isbn_13)
