from django.urls import path
from .views import ReleaseListView, ReleaseCreateView, ReleaseDiscussionIdentifierGetView

urlpatterns = [
    path('list', ReleaseListView.as_view(), name='release-list'),
    path('create', ReleaseCreateView.as_view(), name='release-create'),
    path('<int:release_id>', ReleaseDiscussionIdentifierGetView.as_view(), name='release-get-identifier'),
]