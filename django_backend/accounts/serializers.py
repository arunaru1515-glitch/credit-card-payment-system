from rest_framework import serializers
from .models import Card, User, AuditLog
from django.contrib.auth import authenticate


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(default=User.ROLE_CUSTOMER, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

    def create(self, validated_data):
        role = validated_data.get('role', User.ROLE_CUSTOMER)
        valid_roles = dict(User.ROLE_CHOICES).keys()
        if role not in valid_roles:
            role = User.ROLE_CUSTOMER

        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            role=role
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        user = authenticate(
            username=username,
            password=password
        )

        if user is None:
            raise serializers.ValidationError(
                "Invalid username or password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "User account is inactive."
            )

        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'role',
            'is_active',
            'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']


class CardSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Card
        fields = [
            'id',
            'username',
            'card_type',
            'masked_card_number',
            'last_four_digits',
            'credit_limit',
            'is_blocked',
            'created_at'
        ]
        read_only_fields = [
            'id',
            'username',
            'credit_limit',
            'is_blocked',
            'created_at'
        ]


class AuditLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source='actor.username', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'actor',
            'actor_username',
            'action',
            'target_type',
            'target_id',
            'description',
            'old_value',
            'new_value',
            'ip_address',
            'created_at'
        ]
        read_only_fields = [
            'id',
            'actor',
            'actor_username',
            'action',
            'target_type',
            'target_id',
            'description',
            'old_value',
            'new_value',
            'ip_address',
            'created_at'
        ]