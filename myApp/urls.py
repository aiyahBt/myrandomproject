from django.urls import path
from . import views

app_name = 'myApp'
urlpatterns = [
    path('', views.home, name = 'home'),
    path('home/', views.home, name = 'home'),
    path('search/', views.search, name='search'),
    path('add_to_shelf/<int:isbn_13>/', views.add_to_shelf, name='add_to_shelf'),
    path('add_to_wish_list/<int:isbn_13>/', views.add_to_wish_list, name='add_to_wish_list'),

]