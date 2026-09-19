from rest_framework import serializers
from departments.models import Department
from users.serializers import CustomUserSerializer

class DepartmentSerializer(serializers.ModelSerializer):
    manager_detail = CustomUserSerializer(source='manager', read_only=True)
    teams_count = serializers.IntegerField(source='teams.count', read_only=True)
    users_count = serializers.IntegerField(source='users.count', read_only=True)

    class Meta:
        model = Department
        fields = [
            'id', 'name', 'description', 'manager', 
            'manager_detail', 'teams_count', 'users_count', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
