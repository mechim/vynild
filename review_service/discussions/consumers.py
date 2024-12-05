# consumers.py
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
import requests
import os
from channels.db import database_sync_to_async
from review_service.utilities import cache_get, cache_set

class DiscussionConsumer(AsyncJsonWebsocketConsumer):
    def get_token_from_headers(self, headers, _key):
        for key, value in headers:
            if key == _key:
                return value.decode('utf-8')  # Decode from bytes to string
        return None
    
    async def check_releases(self):
        from releases.models import Release
        try:
            releaases = await database_sync_to_async(Release.objects.get)(discussion_identifier=self.discussion_identifier)
            print(releaases)
            return True
        except Release.DoesNotExist():
            return False
        
    async def fetch_username(self, user_id):
        cache_key = f"user_{user_id}_username"
        cached_username = cache_get(cache_key)
        if cached_username:
            print(f"found cached username for user #{user_id}")
            return cached_username

         # Fetch the username from the external microservice
        user_service_url = f'{os.getenv('API_GATEWAY_URL')}user-service/users/list?id={user_id}'  # Replace with actual user service URL
        
        try:
            response = requests.get(user_service_url)
            if response.status_code == 200:
                user_data = response.json()
                username = user_data[0].get('username')
                cache_set(cache_key, username, timeout=3600)
                print(f"cached username for user #{user_id}")
                return  username # Assuming the response contains a 'username' field
            else:
                return "Unknown"  # Handle cases where the user is not found
        except requests.exceptions.RequestException:
            return "Service Unavailable"  # Handle connection errors    
        
    async def connect(self):
        await self.accept()
        self.discussion_identifier = self.scope['url_route']['kwargs']['discussion_identifier']
        print(self.discussion_identifier)
        self.discussion_group_name = f'chat_{self.discussion_identifier}'
        # find if exists in database object releases by disc identifier
        # by user id get username
        user_id = self.get_token_from_headers(self.scope["headers"], b"x-user-id")  # Assuming you're sending user-id in headers
        self.username = "Unknown"
        if user_id:
            # user_id = user_id.decode('utf-8')  # Decode to string
            # Fetch username for the connected user
            self.username = await self.fetch_username(user_id)

        print(self.username, user_id)
        if self.username in ["Unknown", "Service Unavailable"]:
            await self.send_json({
                'message': 'error: such a user does not exist'
            })
            await self.close()
            return

        if not await self.check_releases():
            await self.send_json({
                'message': 'error: such a discussion doesnt exist'
            })
            await self.close()
            return
        

        # Join the room group
        await self.channel_layer.group_add(
            self.discussion_group_name,
            self.channel_name
        )

        # Send message to the room group
        await self.channel_layer.group_send(
            self.discussion_group_name,
            {
                'type': 'chat_message',
                'message': f'{self.username}: joined!'
            }
        )

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.discussion_group_name,
            self.channel_name
        )

        # Send message to the room group
        await self.channel_layer.group_send(
            self.discussion_group_name,
            {
                'type': 'chat_message',
                'message': f'{self.username}: left :('
            }
        )

    # Receive message from WebSocket
    async def receive_json(self, content):
        message = content.get('message', '')

        # Send message to the room group
        await self.channel_layer.group_send(
            self.discussion_group_name,
            {
                'type': 'chat_message',
                'message': f'{self.username}: {message}'
            }
        )

    # Receive message from the room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send_json({
            'message': message
        })
