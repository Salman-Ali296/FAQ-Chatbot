from rest_framework import serializers

from .models import FAQ


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ["id", "question", "answer", "category", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(allow_blank=False, trim_whitespace=True)
