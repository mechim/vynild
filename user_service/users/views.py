from rest_framework import generics
from .models import User
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
