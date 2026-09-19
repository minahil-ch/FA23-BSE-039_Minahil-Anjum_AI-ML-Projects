from rest_framework import serializers
from users.models import CustomUser, UserRole
from departments.models import Department
from teams.models import Team

class CustomUserSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'role', 'phone_number', 'department', 'department_name',
            'team', 'team_name', 'avatar', 'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined', 'is_active']

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 'last_name', 'phone_number']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        # Standard users are registered as Employee by default
        user = CustomUser.objects.create(
            role=UserRole.EMPLOYEE,
            **validated_data
        )
        user.set_password(password)
        user.save()
        return user
