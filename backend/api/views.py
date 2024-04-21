from django.utils import timezone
from rest_framework import mixins, viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.hashers import make_password
from rest_framework.throttling import AnonRateThrottle

from .serializers import (
    AuthTokenSerializer,
    UserRegistrationSerializer,
    UserSerializer
)
from users.models import User, AuthCode, UserManager
from users.utils import generate_code
from .throttles import LowRequestThrottle


class UserViewSet(mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    serializer_class = UserRegistrationSerializer
    # throttle_classes = [AnonRateThrottle, LowRequestThrottle, ]
    permission_classes = (~IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        if not (phone_number := request.data.get('phone_number')):
            return Response(
                data='Email must be provided.',
                status=status.HTTP_400_BAD_REQUEST
            )

        if not (user := User.objects.filter(phone_number=phone_number).first()):
            def generate_referral_code():
                code = generate_code(length=6, referral=True)
                if User.objects.filter(ref_code=code).exists():
                    code = generate_referral_code()
                return code

            ref_code = generate_referral_code()
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid(raise_exception=True):
                return Response(serializer)
            user = serializer.save(ref_code=ref_code)

        authorization_code = generate_code()
        hasher_code = make_password(
            authorization_code,
            salt=None,
            hasher='default'
        )
        AuthCode.objects.create(
            user=user,
            code=hasher_code,
            datetime_end=timezone.now() + timezone.timedelta(minutes=30)
        )
        # TODO: Тут должна вызываться задача отправки кода.
        print(authorization_code)
        return Response(
            data='The authorization code has been sent by phone.',
            status=status.HTTP_201_CREATED
        )

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me'
    )
    def get_current_user_info(self, request):
        serializer = UserSerializer(request.user)
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )

    @get_current_user_info.mapping.patch
    def update_user_info(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        # TODO: Нужно добавить возможность стать рефералом.
        serializer.save()
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @action(
        methods=['post'],
        detail=False
    )
    def login(self, request, *args, **kwargs):
        """
        Create user authorization token.
        """
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['obj']
        if code.used:
            # Проверка: Не был ли код активирован
            # ранее (поле used = False).
            return Response(
                data='The code has used.',
                status=status.HTTP_400_BAD_REQUEST
            )
        if code.datetime_end < timezone.now():
            # Проверка: Код действует (текущая дата
            # меньше чем дата в поле datetime_end).
            return Response(
                data='The code has expired.',
                status=status.HTTP_400_BAD_REQUEST
            )
        user = User.objects.get(phone_number=request.data['phone_number'])
        token, created = Token.objects.get_or_create(user=user)
        # После создания токена меняем статус used на True.
        code.used = True
        code.save()
        return Response({'token': token.key})

    @action(
        methods=['delete'],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def logout(self, request, *args, **kwargs):
        """
        Delete user authorization token.
        """
        # Удалить токен.
        user_token = request.user.auth_token
        user_token.delete()
        return Response(
            data='The authorization token has been removed.',
            status=status.HTTP_204_NO_CONTENT

        )