from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import CustomUser, UserRole
from users.serializers import CustomUserSerializer, UserRegisterSerializer
from users.permissions import IsAdmin, IsManager
from activity_logs.models import ActivityLog

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT Token Obtain view that logs a user login activity.
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            username = request.data.get('username')
            try:
                user = CustomUser.objects.get(username=username)
                ActivityLog.objects.create(
                    user=user,
                    action="USER_LOGIN",
                    details={"message": f"User {username} logged in successfully via JWT."},
                    ip_address=self.get_client_ip(request)
                )
            except CustomUser.DoesNotExist:
                pass
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class RegisterView(APIView):
    """
    API View to register new users.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            ActivityLog.objects.create(
                user=user,
                action="USER_REGISTER",
                details={"message": f"User {user.username} registered in the system."},
                ip_address=self.get_client_ip(request)
            )
            return Response(CustomUserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class LogoutView(APIView):
    """
    API View to log out users and blacklist their refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            ActivityLog.objects.create(
                user=request.user,
                action="USER_LOGOUT",
                details={"message": f"User {request.user.username} logged out."},
                ip_address=self.get_client_ip(request)
            )
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = CustomUser.objects.all().order_by('-date_joined')
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action in ['me', 'update_me']:
            return [permissions.IsAuthenticated()]
        return [IsAdmin()]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Retrieve current logged in user details.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['patch', 'put'])
    def update_me(self, request):
        """
        Update current logged in user profile details.
        """
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            ActivityLog.objects.create(
                user=user,
                action="USER_PROFILE_UPDATE",
                details={"message": f"User {user.username} updated their profile info."},
                ip_address=request.META.get('REMOTE_ADDR')
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
