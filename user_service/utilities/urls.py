from django.urls import path 
from .views import StatusCheckView, SleepyView

urlpatterns = [
    path('status', StatusCheckView.as_view(), name='status'),
    path('sleep', SleepyView.as_view(), name='sleep')
]