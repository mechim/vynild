import time
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
class SleepyView(APIView):
    def get(self, request):
        if not int(os.getenv('AWAKE_INSTANCE', 1)):
            time.sleep(int(os.getenv('SLEEP_DURATION_S', 10)))

        return response.Response(
            {'message': "Sleepy Time! hee hee... You are not supposed to see this message!"},
            status=status.HTTP_202_ACCEPTED
        )
    