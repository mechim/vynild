import requests
from rest_framework import serializers
from .models import Review
from releases.serializers import RealeaseListSerializer
import os
from django.core.cache import cache

class ReviewListSerializer(serializers.ModelSerializer):
    release = RealeaseListSerializer(read_only=True)
    def fetch_username(self, obj):
        cache_key = f"user_{obj.user_id}_username"
        cached_username = cache.get(cache_key)
        if cached_username:
            return cached_username

         # Fetch the username from the external microservice
        user_service_url = f'{os.getenv('API_GATEWAY_URL')}users/list?id={obj.user_id}'  # Replace with actual user service URL
        
        try:
            response = requests.get(user_service_url)
            if response.status_code == 200:
                user_data = response.json()
                username = user_data[0].get('username')
                cache.set(cache_key, username, timeout=3600)
                return  username # Assuming the response contains a 'username' field
            else:
                return "Unknown"  # Handle cases where the user is not found
        except requests.exceptions.RequestException:
            return "Service Unavailable"  # Handle connection errors    
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['username'] = self.fetch_username(instance)  # Populate the username field
        return representation
    
    class Meta:
        model = Review
        fields = ['id', 'release', 'review_text', 'review_mark']


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['user_id', 'release', 'review_text', 'review_mark']
