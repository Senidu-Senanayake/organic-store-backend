from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    CustomerProfileSerializer, ModeratorProfileSerializer, WarehouseManagerProfileSerializer
)
from .models import CustomerProfile, ModeratorProfile, WarehouseManagerProfile

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class CustomerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = CustomerProfile.objects.get_or_create(user=self.request.user)
        return profile


class ModeratorListView(generics.ListCreateAPIView):
    queryset = ModeratorProfile.objects.all()
    serializer_class = ModeratorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_admin:
            return ModeratorProfile.objects.all()
        return ModeratorProfile.objects.none()


class WarehouseManagerListView(generics.ListCreateAPIView):
    queryset = WarehouseManagerProfile.objects.all()
    serializer_class = WarehouseManagerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_admin:
            return WarehouseManagerProfile.objects.all()
        return WarehouseManagerProfile.objects.none()