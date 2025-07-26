from rest_framework import serializers

from rest_framework import serializers


class EmailSerializer(serializers.Serializer):
    recipient_list = serializers.ListField(
        child=serializers.EmailField(),
        allow_empty=False,
    )
    email_type = serializers.CharField(required=True)
    subject = serializers.CharField(required=True)
    context = serializers.DictField(required=False, allow_null=True, default=dict)
