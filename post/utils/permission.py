from rest_framework.permissions import BasePermission


class IsSenderOrReceiver(BasePermission):
    """
    Allows access only if the user is the sender or receiver of the follow request.
    """

    def has_object_permission(self, request, view, obj):
        return request.user and (request.user == obj.sender or request.user == obj.receiver)
