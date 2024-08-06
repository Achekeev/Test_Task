from .models import User, Article
from rest_framework import serializers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid email format")
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one digit")
        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError("Password must contain at least one letter")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author']
        read_only_fields = ['author']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        return super().create(validated_data)