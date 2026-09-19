from rest_framework import serializers
from tasks.models import Task
from users.serializers import CustomUserSerializer
from departments.serializers import DepartmentSerializer

class TaskSerializer(serializers.ModelSerializer):
    assigned_to_detail = CustomUserSerializer(source='assigned_to', read_only=True)
    department_detail = DepartmentSerializer(source='department', read_only=True)
    created_by_detail = CustomUserSerializer(source='created_by', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority', 
            'assigned_to', 'assigned_to_detail', 
            'department', 'department_detail', 
            'created_by', 'created_by_detail', 
            'due_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
