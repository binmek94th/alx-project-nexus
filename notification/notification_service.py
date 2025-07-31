import uuid


def send_notification(user_id):
    """
    Sends a notification to a specific user via WebSocket.

    Args:
        user_id (uuid): The ID of the user to send the notification to.
    """
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    message = get_notifications(user_id)
    channel_layer = get_channel_layer()
    group_name = str(user_id).strip()
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send_notification",
            "message": message,
        }
    )


def get_notifications(user_id):
    """
    Retrieves notifications for a specific user.

    Args:
        user_id (uuid): The ID of the user whose notifications are to be retrieved.

    Returns:
        list: A list of serialized notification data.
    """
    from notification.models import Notification
    from notification.serializers import NotificationSerializer

    notifications = Notification.objects.filter(user_id=user_id).filter(is_read=False).order_by('-created_at')
    serializer = NotificationSerializer(notifications, many=True)

    data = serializer.data
    for notification in data:
        if 'id' in notification and isinstance(notification['id'], uuid.UUID):
            notification['id'] = str(notification['id'])
    return data
