from django.contrib.auth.hashers import check_password
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from users.models import User, AuthCode


class AuthTokenSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        label=_("Phone number"),
        write_only=True
    )
    code = serializers.CharField(
        label=_("Code"),
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        code = attrs.get('code')

        if phone_number and code:
            if not (obj := AuthCode.objects.filter(
                user__phone_number=phone_number
            ).first()):
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')

            if not check_password(code, obj.code):
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "phone number" and "code".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['obj'] = obj
        return attrs


class UserRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'phone_number',
        )

    def to_representation(self, instance):
        """Переопределение сериализатора для выходных данных."""
        return UserShortSerializer(
            instance, context=self.context
        ).data


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'phone_number',
            'first_name',
            'last_name',
        )


class UserShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'phone_number',
        )
