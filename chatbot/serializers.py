from rest_framework import serializers
from .models import ChatSession

class MessageSerializer(serializers.Serializer):
    question = serializers.CharField(help_text='사용자 메시지')
    session_id = serializers.CharField(help_text='세션 ID', required=False)


class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ['session_id', 'start_time', 'end_time', 'chat_history']