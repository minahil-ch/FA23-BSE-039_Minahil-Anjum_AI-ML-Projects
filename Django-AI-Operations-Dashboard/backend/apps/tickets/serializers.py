from rest_framework import serializers
from tickets.models import Ticket
from users.serializers import CustomUserSerializer

class TicketSerializer(serializers.ModelSerializer):
    created_by_detail = CustomUserSerializer(source='created_by', read_only=True)
    assigned_to_detail = CustomUserSerializer(source='assigned_to', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'subject', 'description', 'status', 'priority',
            'created_by', 'created_by_detail',
            'assigned_to', 'assigned_to_detail',
            'ai_category', 'ai_priority', 'ai_department', 'ai_confidence',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_by', 'ai_category', 'ai_priority',
            'ai_department', 'ai_confidence', 'created_at', 'updated_at',
        ]
