from reviews.models import User
from rest_framework import serializers, exceptions
from rest_framework.validators import UniqueValidator
from api_yamdb.settings import (MESSAGE_FOR_RESERVED_NAME,
                                RESERVED_NAME,
                                MESSAGE_FOR_USER_NOT_FOUND)


class ForUserAndAdminSerializer(serializers.ModelSerializer):
    """Сериалайзер для пользователей со статусом user и admin.
    Зарезервированное имя использовать нельзя."""
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Этот адрес электроной почты уже используется'
        )]
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )

    def validate_username(self, value):
        if value == RESERVED_NAME:
            raise serializers.ValidationError(MESSAGE_FOR_RESERVED_NAME)
        return value


class UsersMeSerializer(ForUserAndAdminSerializer):
    """Сериалайзер для редактирования обычного пользователя."""
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )


class SendCodeUserSerializer(serializers.ModelSerializer):
    """Сериалайзер для отправки сообщения на почту."""
    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена.
    Зарезервированное имя использовать нельзя."""
    username = serializers.CharField(max_length=200, required=True)
    confirmation_code = serializers.CharField(max_length=200, required=True)

    def validate_username(self, value):
        if value == RESERVED_NAME:
            raise serializers.ValidationError(MESSAGE_FOR_RESERVED_NAME)
        if not User.objects.filter(username=value).exists():
            raise exceptions.NotFound(MESSAGE_FOR_USER_NOT_FOUND)
        return value
