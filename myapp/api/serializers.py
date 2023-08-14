import os
import re

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, smart_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import serializers
from myapp.models import CustomUser, PostModel, LikesModel, CommentModel
from django.core.mail import EmailMessage

from datetime import date


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'dob', 'password', 'phone', 'image', 'bio']

    def validate_dob(self, value):
        if value >= date.today():
            raise serializers.ValidationError("Date shouldn't be greater than today")
        return value

    def validate_phone(self, value):
        phone = value
        pattern = r'\d{10}'
        if not re.match(pattern, phone):
            raise serializers.ValidationError("Please Enter Proper Phone Number!")
        return phone

    def validate_first_name(self, value):
        fname = value
        if not fname.isalpha():
            raise serializers.ValidationError("Please Enter Character")
        return fname

    def validate_last_name(self, value):
        lname = value
        if not lname.isalpha():
            raise serializers.ValidationError("Please Enter Character")
        return lname

    def create(self, validated_data):
        user = CustomUser.objects.create(first_name=validated_data['first_name'], last_name=validated_data['last_name'],
                                         email=validated_data['email'], image=validated_data['image'],
                                         bio=validated_data['bio'], phone=validated_data['phone'],
                                         dob=validated_data['dob'])
        user.set_password(validated_data['password'])
        user.save()
        return user


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostModel
        fields = ['id', 'caption', 'post_image', 'created_at', 'updated_at', 'user']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentModel
        fields = ['id', 'user', 'post', 'comment', 'created_at', 'updated_at']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=255)
    new_password = serializers.CharField(max_length=255)
    new_password1 = serializers.CharField(max_length=255)

    def validate_old_password(self, value):
        user = self.context.get('user')
        old_password = value
        if not user.check_password(old_password):
            raise serializers.ValidationError('Old Password Is Not Correct.')
        return value

    def validate(self, validate_data):
        user = self.context.get('user')
        new_password = validate_data.get('new_password')
        new_password1 = validate_data.get('new_password1')
        if new_password != new_password1:
            raise serializers.ValidationError('Both Password Not Matching.')
        user.set_password(new_password)
        user.save()
        return validate_data


class SendResetLinkSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']

    def validate_email(self, value):
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email is Not Valid')
        return value

    def validate(self, attrs):
        email = attrs.get('email')
        user = CustomUser.objects.get(email=email)
        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        url = f'http://127.0.0.1:8000/api/users/reset/{uid}/{token}/'
        body = f"""Hey, 
            You're receiving this email because you requested a password reset for your account at Attendance System.\n
            Please go to the following page and choose a new password:\n
            {url}\n
            Thanks for using our site!\n
            The itpathsolutions team"""
        # body ="<html><body><h1>Welcome</h1></body></html>"
        email = EmailMessage(subject='Reset your password', body=body, to=[user.email],
                             from_email=os.environ.get('HOST_USER'))
        # email.content_subtype="html"
        email.send()
        return attrs


class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255)
    password1 = serializers.CharField(max_length=255)

    def validate(self, validate_data):
        try:
            uid = self.context.get('uid')
            token = self.context.get('token')
            password = validate_data.get('password')
            password1 = validate_data.get('password1')
            if password != password1:
                raise serializers.ValidationError('Both Password Not Matching.')

            id = smart_str(urlsafe_base64_decode(uid))
            user = CustomUser.objects.filter(id=id).first()
            if not user:
                raise serializers.ValidationError('Uid is Not Valid')
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('Token is not valid or Expired')
            user.set_password(password)
            user.save()
            return validate_data
        except DjangoUnicodeDecodeError as identifier:
            raise serializers.ValidationError('Token is not Valid or Expired')


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'email', 'dob', 'phone', 'image', 'bio']
