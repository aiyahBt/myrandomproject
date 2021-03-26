from django.urls import path
from . import views

app_name = 'user'
urlpatterns = [
    path('user', views.shelf_view, name = 'shelf'),

    path('user/shelf', views.shelf_view, name = 'shelf'),

    path('user/wish_list', views.wish_list_view, name='wish_list'),

    path('user/request_exchange/<int:isbn_13>/', views.request_exchange, name='request_exchange'),

    path('user/in_request/', views.in_request_view, name='in_request'),

    path('user/request/<int:request_id>/<int:book_1_isbn_13>/<int:denied>/<int:accepted>/', views.request_detail_view, name='request_detail'),

    path('user/active_exchange/', views.active_exchange_view, name='active_exchange'),
    path('user/exchange_detail/<int:id>', views.exchange_detail_view, name='exchange_detail'),

    # path('add_to_shelf/<int:isbn_13>/', views.add_to_shelf, name='add_to_shelf'),
    # path('add_to_wish_list/<int:isbn_13>/', views.add_to_wish_list, name='add_to_wish_list'),

]