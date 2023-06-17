from rest_framework import serializers
from account.models import Account
from photo.models import Photo
from django.core.exceptions import ValidationError
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone
from rest_framework.exceptions import ParseError

class AccountPhotoUploadSerializer(serializers.Serializer):
    file = serializers.ImageField()

class AccountRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)

    class Meta:
        model = Account
        fields = ['username', 'nickname', 'email', 'account_photo', 'birth_date', 'password', 'password2']
        extra_kwargs = {
            'password' : {'write_only':True}
        }
    
    # def validate(self, attrs):
    #     password = attrs.get('password')
    #     password2 = attrs.get('password2')

    #     if password != password2:
    #         raise serializers.ValidationError('Both passwords should be equal')
    #     return attrs
    
    def create(self, validated_data):
        account_photo = validated_data.pop('account_photo', None)
        password = validated_data.pop('password', None)
        password2 = validated_data.pop('password2', None)

        if password != password2:
            raise serializers.ValidationError('Both passwords should be equal')

        try:
            user = Account.objects.create_user(**validated_data)
            user.set_password(password)
            user.save()
        except ParseError:
            raise serializers.ValidationError('Invalid image file')

        if account_photo:
            user.account_photo = account_photo
            user.save()

        return user

class AccountLoginSerializer(serializers.ModelSerializer):
    nickname_or_email = serializers.CharField(max_length=32)

    class Meta:
        model = Account
        fields = ['nickname_or_email', 'password']

class AccountGetPublic(serializers.ModelSerializer):

    subscribers_count = serializers.SerializerMethodField('get_subscribers_count')
    posts_count = serializers.SerializerMethodField('get_posts_count')
    photos_count = serializers.SerializerMethodField('get_photos_count')

    def get_subscribers_count(self, account):
        return account.subscribers.count()
    
    def get_posts_count(self, account):
        return account.related_posts.count()
    
    def get_photos_count(self, account):
        return Photo.objects.filter(author=account).count()

    class Meta:
        model = Account
        fields = ['username', 'nickname', 'birth_date', 'created_at', 'is_verify', 'is_blocked', 'account_photo', 'account_banner', 'city', 'country', 'links', 'subscribers_count', 'posts_count', 'photos_count']

class AccountGetPrivate(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['nickname', 'birth_date', 'city', 'country', 'email']