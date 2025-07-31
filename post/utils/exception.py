from rest_framework.exceptions import APIException
from rest_framework import status


class FollowRequestSent(APIException):
    """
    Exception raised when a follow request is sent successfully.
    This exception is used to indicate that a follow request has been sent to the user.
    """
    status_code = status.HTTP_202_ACCEPTED
    default_detail = 'Follow request sent.'
    default_code = 'follow_request_sent'
