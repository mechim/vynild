from django.urls import path 
from .views import ReviewCreateView, ReviewListView

urlpatterns = [
    path('create', ReviewCreateView.as_view(), name='create'),
    path('list', ReviewListView.as_view(), name='list')
]