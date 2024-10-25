from django.urls import path 
from .views import StatusCheckView

urlpatterns = [
    path('status', StatusCheckView.as_view(), name='status')
]