from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status
from .permissions import IsOwner

from decouple import config

DEBUG = config('DEBUG', cast=bool)

# View Starts here

class LandingPageAPI(APIView):
    if DEBUG:
        permission_classes = (permissions.AllowAny,)
    else:
        permission_classes = (permissions.IsAuthenticated, IsOwner,)
    
    def get(self, request):
        user = request.user
        return Response({"hello":"hello"},status=status.HTTP_200_OK)