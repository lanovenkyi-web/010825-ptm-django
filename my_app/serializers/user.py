import re
from datetime import date
from typing import Any

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from my_app.models import User



class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        write_only=True,
        max_length=30,
        trim_whitespace=True
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        max_length=30,
    )

    def validate(self, attrs: dict[str, str]) -> dict[str, Any]:
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError(
                {
                    "message": "Must include both username and password to log in"
                }
            )

        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password
        )

        if not user:
            raise serializers.ValidationError(
                {
                    "message": "Incorrect username or password"
                }
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {
                    "message": "User account is disabled"
                }
            )

        if user.deleted:
            raise serializers.ValidationError(
                {
                    "message": "User account is deleted"
                }
            )

        attrs['user'] = user
        return attrs


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        trim_whitespace=False,
    )
    re_password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        trim_whitespace=False,
    )
    gender = serializers.ChoiceField(
        choices=User.Gender,
        required=True,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "re_password",
            "first_name",
            "last_name",
            "phone",
            "birth_date",
            "gender",
        ]

    def validate_username(self, value: str) -> str:
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Username is required.")

        if len(value) < 3:
            raise serializers.ValidationError(
                "Username must contain at least 3 characters."
            )

        return value

    def validate_email(self, value: str) -> str:
        value = value.strip().lower()

        if not value:
            raise serializers.ValidationError("Email is required.")

        return value

    def validate_first_name(self, value: str | None) -> str | None:
        if value in (None, ""):
            return value

        value = value.strip()

        if not re.fullmatch(r"^[a-zA-Z]+(?:[-'][a-zA-Z]+)*$", value):
            raise serializers.ValidationError(
                "First name must contain only alphabet characters."
            )

        return value

    def validate_last_name(self, value: str | None) -> str | None:
        if value in (None, ""):
            return value

        value = value.strip()

        if not re.fullmatch(r"^[a-zA-Z]+(?:[-'][a-zA-Z]+)*$", value):
            raise serializers.ValidationError(
                "Last name must contain only alphabet characters."
            )

        return value

    def validate(self, attrs):
        password = attrs.get("password")
        re_password = attrs.pop("re_password", None)
        birth_date = attrs.get("birth_date")

        try:
            validate_password(password)
        except ValidationError as e:
            msg = str(e.messages[0])
            raise serializers.ValidationError(
                {"password": msg},
                code="authorization",
            )

        if password != re_password:
            raise serializers.ValidationError(
                {"re_password": "Passwords do not match."}
            )

        if birth_date is not None:
            today = date.today()
            attrs["age"] = (
                today.year
                - birth_date.year
                - ((today.month, today.day) < (birth_date.month, birth_date.day))
            )
        else:
            attrs["age"] = None

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data["role"] = User.Role.lib_member

        user = User.objects.create_user(
            password=password,
            is_staff=False,
            is_active=True,
            deleted=False,
            **validated_data,
        )

        return user


class UserListSerializer(serializers.ModelSerializer):
    books_count = serializers.IntegerField(required=False, read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'gender',
            'date_joined',
            'books_count',
            'deleted',
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone',
            'role',
            'gender',
            'is_staff',
            'is_active',
            'date_joined',
        ]


class PromoteModeratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['is_staff', 'role']

        extra_kwargs = {
            'is_staff': {'required': True},
            'role': {'required': True},
        }

    def validate_role(self, value: str) -> str:
        if value not in User.Role:
            raise serializers.ValidationError(
                f"Invalid role choice: {value}"
            )
        return value
