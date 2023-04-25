from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.settings import DEFAULT_FROM_EMAIL
from api import permissions
from users.serializers import (ForUserAndAdminSerializer,
                               SendCodeUserSerializer,
                               TokenSerializer,
                               UsersMeSerializer)
from reviews.models import User


def create_confirmation_code_and_send_email(username, to_email):
    """Создаем confirmation code и отправляем по email."""
    user = get_object_or_404(User, username=username)
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        'Код подтверждения',
        f'Ваш код подтверждения {confirmation_code}',
        DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False,
    )


class APISignUp(APIView):
    """Регистрация пользователя."""

    permission_classes = (AllowAny,)

    def post(self, request):
        code_serializer = SendCodeUserSerializer(data=request.data)
        code_serializer.is_valid(raise_exception=True)
        serializer = ForUserAndAdminSerializer(data=request.data)
        data = code_serializer.data
        if not User.objects.filter(username=data['username'],
                                   email=data['email']).exists():
            if serializer.is_valid(raise_exception=True):
                serializer.save(is_active=False)
        # создаем confirmation code и отправляем на почту
        create_confirmation_code_and_send_email(
            data['username'], data['email'])
        return Response(
            {'email': data['email'],
             'username': data['username']},
            status=status.HTTP_200_OK)


class APIToken(APIView):
    """Выдача токена."""

    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = get_object_or_404(
                User, username=serializer.data['username'])
            # проверяем confirmation code, если верный, выдаем токен
            if default_token_generator.check_token(
               user, serializer.data['confirmation_code']):
                token = AccessToken.for_user(user)
                user.is_active = True
                user.save()
                return Response(
                    {'token': str(token)}, status=status.HTTP_200_OK)
            return Response({
                'confirmation code': 'Некорректный код подтверждения!'},
                status=status.HTTP_400_BAD_REQUEST)


class APIUser(APIView):
    """Работа со своими данными для пользователя."""

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=request.user.username)
        serializer = UsersMeSerializer(user, many=False)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=request.user.username)
        serializer = UsersMeSerializer(
            user, data=request.data, partial=True, many=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSetForAdmin(ModelViewSet):
    """Работа с пользователями для администратора."""

    queryset = User.objects.all()
    serializer_class = ForUserAndAdminSerializer
    # поиск по эндпоинту users/{username}/
    lookup_field = 'username'
    permission_classes = (permissions.IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    def update(self, request, *args, **kwargs):
        if request.method == "PUT":
            raise MethodNotAllowed(request.method)
        return super().update(request, *args, **kwargs)
