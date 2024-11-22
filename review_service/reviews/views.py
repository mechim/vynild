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
        

# @method_decorator(csrf_exempt, name='dispatch')
# class BulkAddReviewsAPIView(View):
#     def post(self, request, *args, **kwargs):
#         try:
#             # Parse JSON data from the request body
#             data = json.loads(request.body)

#             # Ensure the payload is a JSON object containing a "reviews" field
#             if not isinstance(data, dict) or "reviews" not in data or not isinstance(data["reviews"], list):
#                 return JsonResponse({"error": "Invalid input format, expected a JSON object with a 'reviews' field containing a list of review objects."}, status=400)

#             reviews = data["reviews"]
#             created_reviews = []
#             errors = []

#             for item in reviews:
#                 try:
#                     user_id = item.get("user_id")
#                     release_id = item.get("release_id")
#                     review_text = item.get("review_text", "")
#                     review_mark = item.get("review_mark")

#                     # Validate required fields
#                     if user_id is None or release_id is None or review_mark is None:
#                         raise ValidationError("user_id, release_id, and review_mark are required.")

#                     # Check if release exists
#                     release = Release.objects.get(pk=release_id)

#                     # Create and save the review
#                     review = Review.objects.create(
#                         user_id=user_id,
#                         release=release,
#                         review_text=review_text,
#                         review_mark=review_mark
#                     )
#                     created_reviews.append({
#                         "id": review.id,
#                         "user_id": review.user_id,
#                         "release_id": review.release.id,
#                         "review_text": review.review_text,
#                         "review_mark": review.review_mark,
#                     })
#                 except Release.DoesNotExist:
#                     errors.append({"error": f"Release with id {item.get('release_id')} does not exist.", "item": item})
#                 except ValidationError as ve:
#                     errors.append({"error": str(ve), "item": item})
#                 except Exception as e:
#                     errors.append({"error": str(e), "item": item})

#             response_data = {
#                 "created_reviews": created_reviews,
#                 "errors": errors,
#             }

#             return JsonResponse(response_data, status=201 if created_reviews else 400)

#         except json.JSONDecodeError:
#             return JsonResponse({"error": "Invalid JSON format."}, status=400)


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