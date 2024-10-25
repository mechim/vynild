from rest_framework import generics
from .models import Release
from .serializers import RealeaseListSerializer, ReleaseCreateSerializer, ReleaseDiscussionIdentifierGetSerializer

class ReleaseListView(generics.ListAPIView):
    queryset = Release.objects.all()
    serializer_class = RealeaseListSerializer

    def get_queryset(self):
        release_id = self.request.query_params.get('id', None)
        if release_id:
            return Release.objects.filter(id=release_id)
        else:
            return Release.objects.all()

class ReleaseCreateView(generics.CreateAPIView):
    queryset = Release.objects.all()
    serializer_class = ReleaseCreateSerializer

class ReleaseDiscussionIdentifierGetView(generics.ListAPIView):
    queryset = Release.objects.all()
    serializer_class = ReleaseDiscussionIdentifierGetSerializer

    def get_queryset(self):
        release_id = self.kwargs.get('release_id')
        return Release.objects.filter(id=release_id)