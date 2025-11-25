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
import requests
from django.conf import settings
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, UpdateProfileSerializer, ChangePasswordSerializer

User = get_user_model()


def home(request):
    """Page d'accueil de l'API"""
    return render(request, 'api/home.html')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_profile(request):
    """Récupérer le profil de l'utilisateur connecté"""
    serializer = UserSerializer(request.user, context={'request': request})
    return Response(serializer.data)


@api_view(['PATCH', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_user_profile(request):
    """Mettre à jour le profil de l'utilisateur connecté"""
    serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        # Retourner les données complètes avec l'avatar
        user_serializer = UserSerializer(request.user, context={'request': request})
        return Response(user_serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_avatar(request):
    """Uploader une image de profil"""
    if 'avatar' not in request.FILES:
        return Response({'error': 'Aucune image fournie.'}, status=status.HTTP_400_BAD_REQUEST)
    
    avatar_file = request.FILES['avatar']
    
    # Vérifier le type de fichier
    if not avatar_file.content_type.startswith('image/'):
        return Response({'error': 'Le fichier doit être une image.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Vérifier la taille (max 5MB)
    if avatar_file.size > 5 * 1024 * 1024:
        return Response({'error': 'L\'image ne doit pas dépasser 5MB.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Sauvegarder l'avatar
    user = request.user
    user.avatar = avatar_file
    user.save()
    
    # Retourner les données utilisateur mises à jour
    serializer = UserSerializer(user, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """Changer le mot de passe de l'utilisateur connecté"""
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Le mot de passe a été modifié avec succès.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            'user': UserSerializer(user, context={'request': request}).data,
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
            'user': UserSerializer(user, context={'request': request}).data,
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


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def google_oauth(request):
    """Authentification via Google OAuth"""
    try:
        # Accepter soit access_token soit credential (JWT)
        access_token = request.data.get('access_token')
        credential = request.data.get('credential')
        
        if not access_token and not credential:
            return Response({'error': 'Token Google ou credential requis.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Si on a un credential (JWT), on doit d'abord obtenir un access_token
        if credential:
            # Vérifier le credential JWT avec Google
            google_token_info_url = 'https://oauth2.googleapis.com/tokeninfo'
            params = {'id_token': credential}
            token_response = requests.get(google_token_info_url, params=params)
            
            if token_response.status_code != 200:
                return Response({'error': 'Credential Google invalide.'}, status=status.HTTP_401_UNAUTHORIZED)
            
            token_data = token_response.json()
            # Utiliser le sub (subject) comme google_id
            google_id = token_data.get('sub')
            email = token_data.get('email')
            first_name = token_data.get('given_name', '')
            last_name = token_data.get('family_name', '')
            picture = token_data.get('picture', '')
            
            if not google_id or not email:
                return Response({'error': 'Informations Google incomplètes.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Chercher ou créer l'utilisateur
            user = None
            try:
                user = User.objects.get(google_id=google_id)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(email=email)
                    if user and not user.google_id:
                        user.google_id = google_id
                        user.save()
                except User.DoesNotExist:
                    username = email.split('@')[0]
                    base_username = username
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username}{counter}"
                        counter += 1
                    
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        google_id=google_id,
                        is_active=True
                    )
            
            if not user:
                return Response({'error': 'Erreur lors de la création/récupération de l\'utilisateur.'}, 
                               status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Générer les tokens JWT
            refresh = RefreshToken.for_user(user)
            access_token_jwt = refresh.access_token
            
            # Enregistrer l'access token dans OutstandingToken
            try:
                decoded_access = jwt.decode(str(access_token_jwt), settings.SECRET_KEY, algorithms=['HS256'])
                jti_access = decoded_access.get('jti')
                if jti_access:
                    OutstandingToken.objects.get_or_create(
                        jti=jti_access,
                        defaults={
                            'user': user,
                            'token': str(access_token_jwt),
                            'created_at': timezone.now(),
                            'expires_at': timezone.now() + timedelta(hours=1),
                        }
                    )
            except Exception:
                pass
            
            return Response({
                'user': UserSerializer(user, context={'request': request}).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(access_token_jwt),
                }
            }, status=status.HTTP_200_OK)
        
        # Si on a un access_token (ancienne méthode)
        if not access_token:
            return Response({'error': 'Token Google requis.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier le token avec Google
        google_user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(google_user_info_url, headers=headers)
        
        if response.status_code != 200:
            return Response({'error': 'Token Google invalide.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        google_data = response.json()
        google_id = google_data.get('id')
        email = google_data.get('email')
        first_name = google_data.get('given_name', '')
        last_name = google_data.get('family_name', '')
        picture = google_data.get('picture', '')
        
        if not google_id or not email:
            return Response({'error': 'Informations Google incomplètes.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Chercher l'utilisateur par google_id ou email
        user = None
        try:
            user = User.objects.get(google_id=google_id)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=email)
                # Si l'utilisateur existe mais n'a pas de google_id, l'ajouter
                if user and not user.google_id:
                    user.google_id = google_id
                    user.save()
            except User.DoesNotExist:
                # Créer un nouvel utilisateur
                username = email.split('@')[0]
                # S'assurer que le username est unique
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    google_id=google_id,
                    is_active=True
                )
                # Note: L'avatar Google peut être téléchargé plus tard si nécessaire
        
        if not user:
            return Response({'error': 'Erreur lors de la création/récupération de l\'utilisateur.'}, 
                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)
        access_token_jwt = refresh.access_token
        
        # Enregistrer l'access token dans OutstandingToken pour pouvoir le blacklister
        try:
            decoded_access = jwt.decode(str(access_token_jwt), settings.SECRET_KEY, algorithms=['HS256'])
            jti_access = decoded_access.get('jti')
            if jti_access:
                OutstandingToken.objects.get_or_create(
                    jti=jti_access,
                    defaults={
                        'user': user,
                        'token': str(access_token_jwt),
                        'created_at': timezone.now(),
                        'expires_at': timezone.now() + timedelta(hours=1),
                    }
                )
        except Exception:
            pass  # Si on ne peut pas enregistrer, on continue
        
        return Response({
            'user': UserSerializer(user, context={'request': request}).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(access_token_jwt),
            }
        }, status=status.HTTP_200_OK)
        
    except requests.RequestException as e:
        return Response({'error': f'Erreur lors de la vérification du token Google: {str(e)}'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'error': f'Erreur lors de l\'authentification Google: {str(e)}'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)