from rest_framework.response import Response
from rest_framework import generics, status
from .models import Review
from .serializers import ReviewListSerializer, ReviewCreateSerializer

from django.http import JsonResponse
from django.views import View
from django.core.exceptions import ValidationError
import json
from releases.models import Release

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

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


class DeleteReviewsByUserAPIView(generics.views.APIView):
    def delete(self, request, user_id):
        try:
            # Fetch the reviews to return them after deletion
            reviews_to_delete = Review.objects.filter(user_id=user_id)
            
            if not reviews_to_delete.exists():
                return Response({
                    "message": f"No reviews found for user ID {user_id}."
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Serialize the reviews
            serialized_reviews = ReviewCreateSerializer(reviews_to_delete, many=True).data
            
            # Delete the reviews
            reviews_to_delete.delete()
            
            return Response({
                "message": f"Successfully deleted {len(serialized_reviews)} review(s) for user ID {user_id}.",
                "deleted_reviews": serialized_reviews
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "An error occurred while deleting reviews.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class BulkAddReviewsAPIView(generics.views.APIView):
    def post(self, request, *args, **kwargs):
        # Ensure the data is an array
        if not isinstance(request.data, list):
            return Response(
                {"error": "Expected an array of objects"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Deserialize and validate the input
        serializer = ReviewCreateSerializer(data=request.data, many=True)
        if serializer.is_valid():
            # Save all validated objects to the database
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # If validation fails, return the errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)