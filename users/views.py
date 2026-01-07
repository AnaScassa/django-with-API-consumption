from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile
from .serializers import UserProfileSerializer, UserSerializer
from django.contrib.auth import get_user_model

class UserProfileViewSet(ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

        
User = get_user_model()

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()  
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]