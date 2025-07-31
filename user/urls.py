from django.urls import path
from rest_framework.routers import DefaultRouter

from user.views import FollowingViewSet, UserViewSet, send_password_reset_email, verify_reset_password_link, \
    change_password_via_email, resend_email_verification_email, verify_email, FollowerViewSet, FollowRequestViewSet

router = DefaultRouter()

router.register('followings', FollowingViewSet, basename='followings')
router.register('followers', FollowerViewSet, basename='followers')
router.register('users', UserViewSet, basename='users')
router.register('follow_requests', FollowRequestViewSet, basename='follow_requests')

urlpatterns = [
    path('password-reset-link/', send_password_reset_email, name='password_reset_email'),
    path('verify-password-reset-link/', verify_reset_password_link, name='verify_reset_password_link'),
    path('change-password-reset-link/', change_password_via_email, name='change_password_reset_link'),
    path("resend_email_verification_email/", resend_email_verification_email,
         name="resend_email_verification_email"),
    path("verify_email/", verify_email, name="verify_email"),
] + router.urls
