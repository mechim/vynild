from rest_framework import generics, status
from .models import User
from rest_framework.response import Response
from .serializers import UserListSerializer, UserCreateSerializer

# User List View (for listing all users)
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()  # Query to retrieve all users
    serializer_class = UserListSerializer  # Use the UserListSerializer
    
    def get_queryset(self):
        user_id = self.request.query_params.get('id', None)
        if user_id:
            return User.objects.filter(id=user_id)
        else:
            return User.objects.all()

# User Create View (for creating a new user)
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()  # Query to interact with User model
    serializer_class = UserCreateSerializer  # Use the UserCreateSerializer

class UserDeleteView(generics.views.APIView):
    def delete(self, request, *args, **kwargs):
        user_id = request.query_params.get('id', None)
        if not user_id:
            return Response({"detail": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response({"detail": f"User with ID {user_id} deleted successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)