from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .permissions import user_auth_required

# View Starts here

class LandingPageAPI(APIView):
    
    permission_classes = user_auth_required()
    
    def get(self, request):
        user = request.user
        return Response({"hello":str(user)},status=status.HTTP_200_OK)