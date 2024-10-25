# routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('discussions/<str:discussion_identifier>', consumers.DiscussionConsumer.as_asgi()),
]
