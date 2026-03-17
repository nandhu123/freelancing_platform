from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile, Job, Application


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user




class FreelancerDashboardSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'username',
            'email',
            'bio',
            'experience',
            'completed_projects',
            'total_earned',
            'is_verified'
        ]

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ['freelancer', 'status', 'applied_at']
        

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'