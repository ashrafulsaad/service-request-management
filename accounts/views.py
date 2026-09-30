
# Create your views here.
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import CreateOfficerSerializer, RegisterSerializer
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsAdmin,IsCitizen

from .serializers import CreateOfficerSerializer, RegisterSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = []


class MeView(APIView):
    permission_classes = [IsAuthenticated]

class CitizenTestView(APIView):
    permission_classes = [IsCitizen]

    def get(self, request):
        return Response({
	    "message": "You are a citizen",
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "role": request.user.role,
        })
class CreateOfficerView(generics.CreateAPIView):
    serializer_class = CreateOfficerSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def perform_create(self, serializer):
        serializer.save()
