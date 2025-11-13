from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
import jwt
from django.conf import settings
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer

User = get_user_model()


def home(request):
    """Page d'accueil de l'API"""
    return render(request, 'api/home.html')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_profile(request):
    """Récupérer le profil de l'utilisateur connecté"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """Inscription d'un nouvel utilisateur"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Enregistrer l'access token dans OutstandingToken pour pouvoir le blacklister
        try:
            decoded_access = jwt.decode(str(access_token), settings.SECRET_KEY, algorithms=['HS256'])
            jti_access = decoded_access.get('jti')
            if jti_access:
                OutstandingToken.objects.get_or_create(
                    jti=jti_access,
                    defaults={
                        'user': user,
                        'token': str(access_token),
                        'created_at': timezone.now(),
                        'expires_at': timezone.now() + timedelta(hours=1),
                    }
                )
        except Exception:
            pass  # Si on ne peut pas enregistrer, on continue
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(access_token),
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    """Connexion d'un utilisateur"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Enregistrer l'access token dans OutstandingToken pour pouvoir le blacklister
        try:
            decoded_access = jwt.decode(str(access_token), settings.SECRET_KEY, algorithms=['HS256'])
            jti_access = decoded_access.get('jti')
            if jti_access:
                OutstandingToken.objects.get_or_create(
                    jti=jti_access,
                    defaults={
                        'user': user,
                        'token': str(access_token),
                        'created_at': timezone.now(),
                        'expires_at': timezone.now() + timedelta(hours=1),
                    }
                )
        except Exception:
            pass  # Si on ne peut pas enregistrer, on continue
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(access_token),
            }
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_user(request):
    """Déconnexion d'un utilisateur (blacklist du refresh token et access token)"""
    try:
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'Refresh token requis.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Blacklister le refresh token
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        # Blacklister aussi l'access token actuel depuis le header Authorization
        try:
            # Récupérer le jti de l'access token actuel
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                access_token_str = auth_header.split(' ')[1]
                decoded_access = jwt.decode(access_token_str, settings.SECRET_KEY, algorithms=['HS256'])
                jti_access = decoded_access.get('jti')
                
                if jti_access:
                    outstanding_token = OutstandingToken.objects.filter(jti=jti_access).first()
                    if outstanding_token:
                        BlacklistedToken.objects.get_or_create(token=outstanding_token)
        except Exception:
            pass
        
        # Blacklister aussi tous les autres tokens outstanding de cet utilisateur
        try:
            user = request.user
            outstanding_tokens = OutstandingToken.objects.filter(user=user)
            
            for outstanding_token in outstanding_tokens:
                if not BlacklistedToken.objects.filter(token=outstanding_token).exists():
                    BlacklistedToken.objects.get_or_create(token=outstanding_token)
        except Exception:
            pass
        
        return Response({'message': 'Déconnexion réussie. Tous les tokens ont été invalidés.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Token invalide: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """Endpoint de vérification de santé de l'API"""
    return Response({
        'status': 'ok',
        'message': 'API KACH-BRIDGE est opérationnelle'
    }, status=status.HTTP_200_OK)
