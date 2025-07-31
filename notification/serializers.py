
from rest_framework import serializers

from notification.models import Notification


class EmailSerializer(serializers.Serializer):
    """
    Serializer for validating email sending requests.
    This serializer checks the recipient list, email type, subject, and context.
    It ensures that the recipient list is not empty and that the email type and subject are provided
    """
    recipient_list = serializers.ListField(
        child=serializers.EmailField(),
        allow_empty=False,
    )
    email_type = serializers.CharField(required=True)
    subject = serializers.CharField(required=True)
    context = serializers.DictField(required=False, allow_null=True, default=dict)


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for validating notification sending requests.
    This serializer checks the recipient list, email type, subject, and context.
    """
    user = serializers.UUIDField(format='hex_verbose')

    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'is_read', 'created_at', 'updated_at', 'notification_type']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        """
        Update the notification instance with the provided validated data.
        This method marks the notification as read if 'is_read' is in the validated data.
        """
        if 'is_read' in validated_data:
            instance.is_read = validated_data['is_read']
        instance.save()
        return instance


class NotificationListSerializer(serializers.Serializer):
    """
    Serializer for serializing notification list.
    """
    notifications = NotificationSerializer(many=True, read_only=True)
