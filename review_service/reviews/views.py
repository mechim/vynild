from rest_framework import generics
from .models import Review
from .serializers import ReviewListSerializer, ReviewCreateSerializer


class ReviewListView(generics.ListAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewListSerializer

    def get_queryset(self):
        review_id = self.request.query_params.get('id', None)
        if review_id:
            return Review.objects.filter(id=review_id)
        else:
            return Review.objects.all()
        
class ReviewCreateView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewCreateSerializer
