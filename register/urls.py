from django.urls import path
from .views import UserEditView

app_name = 'register'

urlpatterns = [
    path('edit_profile/', UserEditView.as_view(), name='edit_profile'),

]