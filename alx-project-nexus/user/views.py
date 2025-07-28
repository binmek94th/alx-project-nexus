import json
from datetime import datetime
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError
from utils.pagination import CursorSetPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from notification.email_services import send_email_service
from user.models import Follow, User, FollowRequest
from user.serializers import FollowingSerializer, UserSerializer, UserPasswordSerializer, UserUpdateSerializer, \
    UserEmailSerializer, FollowingListSerializer, FollowerListSerializer, FollowRequestSerializer
from user.utils.generate_links import generate_password_reset_link, generate_email_confirmation_link
from user.utils.location import get_client_ip, parse_user_agent
from post.utils.permission import IsSenderOrReceiver
from utils.redis_client import redis_client


class UserViewSet(ModelViewSet):
    """
    A viewset for creating, viewing and editing user instances.
    This viewset provides actions for user registration, profile updates,
    password updates, email updates, and email verification.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CursorSetPagination
    ordering = ['username']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    def get_serializer_context(self):
        user = self.request.user
        return {'user': user}

    def get_serializer_class(self):
        user = self.request.user
        if user.is_authenticated and (user.is_staff or user.is_superuser):
            if self.action == 'create':
                return UserSerializer
            elif self.action == 'put' or self.action == 'patch':
                return UserUpdateSerializer
        return UserSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        message = {
            "email_type": "welcome",
            "recipient_list": [instance.email],
            "subject": "Welcome to Our Service",
            "context": {
                "username": instance.username,
                "link": generate_email_confirmation_link(user=instance)
            }
        }
        send_email_service(message)
        channel = f"user_{instance.id}_emails"
        redis_client.publish(channel, json.dumps(message))

    @action(detail=False, methods=['put', 'patch'], url_path='update-password')
    def update_password(self, request, *args, **kwargs):
        user = request.user
        serializer = UserPasswordSerializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            send_email_service({
                "recipient_list": [user.email],
                "email_type": "password_changed",
                "subject": "Password Changed Successfully",
                "context": {
                    "username": user.username
                }
            })
            return Response({"message": "Password updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put', 'patch'], url_path='update-email')
    def update_email(self, request, *args, **kwargs):
        user = request.user
        try:
            serializer = UserEmailSerializer(instance=user, data=request.data, partial=True)
            if serializer.is_valid():
                instance = serializer.save()
                send_email_service({
                    "email_type": "email_verification",
                    "recipient_list": [instance.email],
                    "subject": "Verify Email Change",
                    "context": {
                        "username": instance.username,
                        "link": generate_email_confirmation_link(user=instance)
                    }
                })
                return Response({"message": "Verification Email Sent"})
        except ValueError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put', 'patch'], url_path='update-account')
    def update_account(self, request, *args, **kwargs):
        user_id = request.query_params.get('id')
        user = request.user
        if (user.is_superuser or user.is_staff) and user_id:
            user = User.objects.get(id=user_id)
        serializer = UserUpdateSerializer(instance=user, data=request.data, partial=True, context={'user': user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def send_password_reset_email(request):
    ip = get_client_ip(request)
    device_info = parse_user_agent(request)
    email = request.data.get('email')
    if not email:
        return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
        reset_link = generate_password_reset_link(user)
        send_email_service({
            "recipient_list": [user.email],
            "email_type": "password_reset",
            "subject": "Password Reset Request",
            "context": {
                "username": user.username,
                "reset_link": reset_link,
                "time": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
                "ip": ip,
                "device": device_info
            }
        })
        return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_reset_password_link(request):
    uid = request.data.get('uid')
    token = request.data.get('token')

    try:
        validate_password_reset_link(uid, token)
        return Response({"message": "Password reset link is valid."}, status=status.HTTP_200_OK)
    except Exception as e:
        Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def change_password_via_email(request):
    ip = get_client_ip(request)
    device_info = parse_user_agent(request)
    uid = request.query_params.get('uid')
    token = request.query_params.get('token')
    password = request.data.get('password')
    if not password:
        return Response({"error": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        try:
            validate_password_reset_link(uid, token)
            user_id = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            send_email_service({
                "recipient_list": [user.email],
                "email_type": "password_changed",
                "subject": "Password Changed Successfully",
                "context": {
                    "username": user.username,
                    "time": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
                    "ip": ip,
                    "device": device_info
                }
            })
            return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
        except (ValueError, User.DoesNotExist):
            raise ValidationError("User with this email does not exist.")
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def validate_password_reset_link(uid, token):
    if not uid or not token:
        return Response({"error": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user_id = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=user_id)

        if default_token_generator.check_token(user, token):
            return "Password reset link is valid."
        else:
            raise ValidationError("Invalid reset link.")
    except User.DoesNotExist:
        raise ValidationError("User does not exist.")


@api_view(['POST'])
def resend_email_verification_email(request):
    if 'email' not in request.data:
        return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
    user = get_object_or_404(User, email=request.data['email'])
    if user.email_verified:
        return Response({"message": "Email already verified."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        result = send_email_service({
            'recipient_list': [user.email],
            'email_type': 'email_verification',
            'subject': 'Email Verification',
            'context': {'username': user.username, 'link': generate_email_confirmation_link(user)}
        })

        if result.is_valid():
            return Response("Email sent successful", status=status.HTTP_201_CREATED)
        else:
            return Response(result.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def verify_email(request):
    uid = request.GET.get('uid')
    token = request.GET.get('token')

    if not uid or not token:
        return Response({"error": "Invalid verification link."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user_id = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=user_id)

        if default_token_generator.check_token(user, token):
            user.email_verified = True
            user.is_active = True
            user.save()
            return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

    except User.DoesNotExist:
        return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)


class FollowingViewSet(ModelViewSet):
    """
    A viewset for viewing and editing following instances.
    This viewset provides actions for following and unfollowing users,
    as well as listing the users that a user is following.
    """
    queryset = Follow.objects.all()
    permission_classes = [IsAuthenticated]
    search_fields = ['following__username', 'following__full_name']
    pagination_class = CursorSetPagination
    ordering = ['following__username']

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return Follow.objects.select_related('follower', 'following').filter(follower__id=user_id)
        return Follow.objects.select_related('follower', 'following').filter(follower=self.request.user)

    def get_serializer_context(self):
        return {'user': self.request.user}

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return FollowingListSerializer
        return FollowingSerializer


class FollowerViewSet(ModelViewSet):
    """
    A viewset for viewing and editing follower instances.
    This viewset provides actions for follower and unfollower users,
    as well as listing the users that a user is follower.
    """
    queryset = Follow.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = FollowerListSerializer
    search_fields = ['follower__username', 'follower__full_name']
    pagination_class = CursorSetPagination

    ordering = ['follower__username']

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return Follow.objects.select_related('follower', 'following').filter(following__id=user_id)
        return Follow.objects.select_related('follower', 'following').filter(following=self.request.user)


class FollowRequestViewSet(ModelViewSet):
    """
    A viewset for managing follow requests.
    This viewset provides actions for sending, accepting, and rejecting follow requests.
    It allows users to view their pending follow requests and manage them accordingly.
    """
    queryset = FollowRequest.objects.all()
    permission_classes = [IsAuthenticated | IsSenderOrReceiver]
    serializer_class = FollowRequestSerializer
    pagination_class = CursorSetPagination

    ordering = ['-created_at']

    def get_queryset(self):
        return FollowRequest.objects.filter(Q(receiver=self.request.user) | Q(sender=self.request.user))

    def get_serializer_context(self):
        return {'user': self.request.user}
