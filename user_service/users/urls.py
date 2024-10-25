from django.urls import path
from .views import UserListView, UserCreateView

urlpatterns = [
    path('list', UserListView.as_view(), name='user-list'),         # List all users
    path('create', UserCreateView.as_view(), name='user-create')  # Create a new user
]
