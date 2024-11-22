from django.urls import path 
from .views import ReviewCreateView, ReviewListView, DeleteReviewsByUserAPIView, BulkAddReviewsAPIView

urlpatterns = [
    path('create', ReviewCreateView.as_view(), name='create'),
    path('list', ReviewListView.as_view(), name='list'),
    path('delete-bulk/<int:user_id>', DeleteReviewsByUserAPIView.as_view(), name='delete-bulk'),
    path('create-bulk', BulkAddReviewsAPIView.as_view(), name='create-bulk'),

]