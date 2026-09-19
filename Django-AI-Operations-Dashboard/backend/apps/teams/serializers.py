from rest_framework import serializers
from teams.models import Team
from users.serializers import CustomUserSerializer
from departments.serializers import DepartmentSerializer

class TeamSerializer(serializers.ModelSerializer):
    leader_detail = CustomUserSerializer(source='leader', read_only=True)
    department_detail = DepartmentSerializer(source='department', read_only=True)
    users_count = serializers.IntegerField(source='users.count', read_only=True)

    class Meta:
        model = Team
        fields = [
            'id', 'name', 'department', 'department_detail', 
            'leader', 'leader_detail', 'users_count', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
