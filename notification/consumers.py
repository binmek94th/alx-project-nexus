import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class NotificationConsumer(WebsocketConsumer):
    """
    This consumer manages sending notifications.
    it uses token to authenticate and send notifications.
    after the client is connected it sends notifications.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.token = None

    def connect(self):
        from alx_project_nexus import settings
        from user.models import User
        from jwt import decode as jwt_decode
        from rest_framework_simplejwt.tokens import UntypedToken
        from notification.notification_service import send_notification

        self.token = self.scope['url_route']['kwargs']['token']

        try:
            UntypedToken(self.token)
        except Exception as e:
            self.accept()
            self.send(text_data=json.dumps({"error": str(e)}))
            self.close()

        decoded_data = jwt_decode(
            self.token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )

        user_id = decoded_data.get("user_id")
        self.user = User.objects.get(id=user_id)
        group_name = str(self.user.id).strip()

        async_to_sync(self.channel_layer.group_add)(
            group_name, self.channel_name
        )
        send_notification(self.user.id)
        self.accept()
        print(f"WebSocket connected to user: {self.user.id}")

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.user.id, self.channel_name
        )

    def send_notification(self, event):
        message = event["message"]
        self.send(text_data=json.dumps(message))
