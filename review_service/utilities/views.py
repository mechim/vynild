from rest_framework.views import APIView
from rest_framework import status, response
import os
PORT = os.getenv('PORT')

class StatusCheckView(APIView):
    def get(self, request):
        return response.Response(
            {
                "status" : "ok",
                "port" : PORT
            },
            status=status.HTTP_200_OK
        )
