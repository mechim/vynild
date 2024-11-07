from rest_framework import serializers
from .models import Release


class RealeaseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Release
        fields = ['id', 'release_name', 'artist_name']

class ReleaseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Release
        fields = ['release_name', 'artist_name']
    
    def create(self, validated_data):
        return Release.objects.create(**validated_data)
    
class ReleaseDiscussionIdentifierGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Release
        fields = ['discussion_identifier', 'connect_url']