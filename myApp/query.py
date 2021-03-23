from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

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

