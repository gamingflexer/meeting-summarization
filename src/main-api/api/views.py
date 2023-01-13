from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status
from .permissions import IsOwner

# Create your views here.

class LandingPageAPI(APIView):
    permission_classes = (permissions.IsAuthenticated, IsOwner,)
    
    def get(self, request):
        user = request.user
        return Response({"hello":"hello"},status=status.HTTP_200_OK)