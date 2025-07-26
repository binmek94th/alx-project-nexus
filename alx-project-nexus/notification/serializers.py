
from rest_framework import serializers


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
