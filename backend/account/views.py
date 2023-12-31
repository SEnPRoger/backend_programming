from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializers import *
from django.contrib.auth import authenticate, login
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FileUploadParser
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import localdate
import requests
from pathlib import Path
from django.conf import settings
import datetime, time
from JWTAuth.views import JWTToken
from account.models import Account
from django.middleware import csrf

# Create your views here.
class AccountRegister(APIView):
    def post(self, request, format=None):
        serializer = AccountRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            account = serializer.save()

            file = request.data.get('account_photo')
            if file is not None:
                extension = str(file).split('.')[1]
            
                if extension == 'gif' and request.user.is_moderator == False:
                    return Response({'status':'you cannot upload gif as account photo'},
                                    status=status.HTTP_200_OK)
            else:
                account.account_photo = file
                account.save()

            #account = serializer.create(serializer.validated_data)
            refresh_token, access_token = JWTToken.generate_tokens(user_id=account.id)
            response = Response({'status':'successfully registered',
                                'access_token':access_token},
                                status=status.HTTP_200_OK)
            JWTToken.set_refresh_to_header(response, refresh_token, header_name='REFRESH-TOKEN')
            response['X-CSRFToken'] = csrf.get_token(request)
                
            return response
        else:
            return Response({'status':'register failed',
                         'error':serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

class AccountLogin(APIView):
    def post(self, request, format=None):
        serializer = AccountLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):

            nickname_or_email = serializer.data.get('nickname_or_email')
            password = serializer.data.get('password')

            account = authenticate(request, nickname=nickname_or_email, password=password)
            if account is not None:
                login(request, account)
                refresh_token, access_token = JWTToken.generate_tokens(user_id=account.id)
                response = Response({'status':'successfully logged',
                                    'access_token':access_token},
                                    status=status.HTTP_200_OK)
                JWTToken.set_refresh_to_header(response, refresh_token, header_name='REFRESH-TOKEN')
                response['X-CSRFToken'] = csrf.get_token(request)
                return response
            else:
                return Response({'status':'account not found!'},
                                    status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'status':'login failed',
                         'error':serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

class AccountView(APIView):
    def get(self, request, nickname=None, format=None):
        try:
            account = Account.objects.get(nickname=nickname)
            if request.user.is_authenticated:
                if account.blocked_accounts.filter(id=request.user.id).exists():
                    return Response(
                        {'status': 'failed',
                        'detail': 'you have been blocked by the owner of the account'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            serializer = AccountGetPublic(account)
        except ObjectDoesNotExist:
            return Response({'status':'failed',
                             'detail':'profile not found'},
                             status=status.HTTP_200_OK)
        return Response({'status':'success',
                             'data':serializer.data,
                             'profile':request.user.nickname},
                             status=status.HTTP_200_OK)
    
class AccountPrivateView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        serializer = AccountGetPrivate(request.user)
        response = Response({'account':serializer.data},
                            status=status.HTTP_200_OK)
        
        response['X-CSRFToken'] = csrf.get_token(request)
        return response