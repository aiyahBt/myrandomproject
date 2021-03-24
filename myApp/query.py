from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import User_Book

 # from myApp.query import query_user

def query_user():
    User = get_user_model()

    # user = User.objects.filter(username='Tubtab')[0]
    # id = user.id
    # print(id)

    users = User.objects.filter(id=5)
    print(users.exists())
    print(users.first())
    print(type(users))
# from myApp.query import query_id
def query_id():
    q_set = User_Book.objects.all()
    n = q_set.count()
    #print(q_set[0].title)
    for i in range(0, n):
        object = q_set[i]
        print(object)
        print(str(object.bookID))



