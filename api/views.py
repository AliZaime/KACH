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
import io
import os
from decouple import config

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
        # Retourner les données complètes
        user_serializer = UserSerializer(request.user, context={'request': request})
        return Response(user_serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Vous pouvez changer en IsAuthenticated si nécessaire
def transcribe_audio(request):
    """
    Transcription audio avec Google Cloud Speech-to-Text
    Supporte le Darija (arabe marocain) avec le code de langue ar-MA
    """
    try:
        # Vérifier si un fichier audio a été envoyé
        if 'audio' not in request.FILES:
            return Response({'error': 'Aucun fichier audio fourni.'}, status=status.HTTP_400_BAD_REQUEST)
        
        audio_file = request.FILES['audio']
        
        # Vérifier la taille du fichier (limite de 10MB)
        if audio_file.size > 10 * 1024 * 1024:
            return Response({'error': 'Le fichier audio est trop volumineux (max 10MB).'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Importer Google Cloud Speech (avec gestion d'erreur si non configuré)
        try:
            from google.cloud import speech
        except ImportError:
            return Response({
                'error': 'Google Cloud Speech-to-Text n\'est pas installé. Installez-le avec: pip install google-cloud-speech'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Configuration des credentials Google Cloud
        # Option 1: Variable d'environnement GOOGLE_APPLICATION_CREDENTIALS
        # Option 2: Chemin vers le fichier JSON dans les settings
        credentials_path = config('GOOGLE_APPLICATION_CREDENTIALS', default='')
        
        # Si un chemin est fourni dans les settings, l'utiliser
        if not credentials_path and hasattr(settings, 'GOOGLE_APPLICATION_CREDENTIALS'):
            credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS
        
        # Initialiser le client Speech-to-Text
        if credentials_path and os.path.exists(credentials_path):
            client = speech.SpeechClient.from_service_account_json(credentials_path)
        else:
            # Essayer d'utiliser les credentials par défaut (variable d'environnement ou Application Default Credentials)
            try:
                client = speech.SpeechClient()
            except Exception as e:
                return Response({
                    'error': f'Erreur de configuration Google Cloud: {str(e)}. '
                            'Assurez-vous que GOOGLE_APPLICATION_CREDENTIALS est configuré ou que '
                            'les Application Default Credentials sont configurées.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Lire le contenu du fichier audio
        audio_content = audio_file.read()
        
        # Détecter le type MIME du fichier
        content_type = audio_file.content_type or 'audio/webm'
        
        # Mapper les types MIME aux encodings Google Cloud Speech
        encoding_map = {
            'audio/webm': speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            'audio/webm;codecs=opus': speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            'audio/ogg': speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            'audio/ogg;codecs=opus': speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            'audio/wav': speech.RecognitionConfig.AudioEncoding.LINEAR16,
            'audio/x-wav': speech.RecognitionConfig.AudioEncoding.LINEAR16,
            'audio/mp3': speech.RecognitionConfig.AudioEncoding.MP3,
            'audio/mpeg': speech.RecognitionConfig.AudioEncoding.MP3,
            'audio/flac': speech.RecognitionConfig.AudioEncoding.FLAC,
        }
        
        # Utiliser WEBM_OPUS par défaut (format le plus courant pour MediaRecorder)
        audio_encoding = encoding_map.get(content_type, speech.RecognitionConfig.AudioEncoding.WEBM_OPUS)
        
        # Configuration de la reconnaissance vocale multilingue
        # Priorité: 1. Darija (ar-MA), 2. Français (fr-FR), 3. Anglais (en-US)
        # Pour WEBM_OPUS et OGG_OPUS, on peut omettre sample_rate_hertz pour la détection automatique
        config_params = {
            'encoding': audio_encoding,
            'language_code': 'ar-MA',  # Langue principale: Darija (arabe marocain)
            'alternative_language_codes': ['fr-FR', 'en-US'],  # Langues secondaires: Français et Anglais
            'enable_automatic_punctuation': True,
            'enable_word_confidence': True,
            'model': 'latest_long',  # Utilise le meilleur modèle pour les enregistrements longs
            # Alternative: 'phone_call' pour les conversations téléphoniques
            # 'model': 'phone_call',
        }
        
        # Ajouter sample_rate_hertz seulement pour les formats qui le nécessitent
        # Pour WEBM_OPUS et OGG_OPUS, Google Cloud peut détecter automatiquement
        if audio_encoding not in [
            speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            speech.RecognitionConfig.AudioEncoding.OGG_OPUS
        ]:
            # Pour les autres formats, utiliser un sample rate standard
            config_params['sample_rate_hertz'] = 44100
        
        config_speech = speech.RecognitionConfig(**config_params)
        
        # Créer l'objet audio
        audio = speech.RecognitionAudio(content=audio_content)
        
        # Effectuer la transcription
        response = client.recognize(config=config_speech, audio=audio)
        
        # Extraire le texte transcrit avec détection de langue
        transcriptions = []
        detected_language = 'ar-MA'  # Par défaut: Darija (langue principale)
        
        for result in response.results:
            alternative = result.alternatives[0]
            transcription_data = {
                'text': alternative.transcript,
                'confidence': alternative.confidence,
            }
            
            # Essayer de détecter la langue depuis les résultats
            # Note: Avec alternative_language_codes, Google Cloud peut retourner 
            # la langue détectée dans language_code si disponible
            if hasattr(result, 'language_code') and result.language_code:
                transcription_data['detected_language'] = result.language_code
                # Utiliser la première langue détectée trouvée
                if detected_language == 'ar-MA':  # Si on n'a pas encore de langue détectée
                    detected_language = result.language_code
            
            transcriptions.append(transcription_data)
        
        # Si aucune transcription n'a été trouvée
        if not transcriptions:
            return Response({
                'text': '',
                'transcriptions': [],
                'detected_language': None,
                'detected_language_name': None,
                'message': 'Aucune transcription trouvée. Assurez-vous que l\'audio contient de la parole.'
            }, status=status.HTTP_200_OK)
        
        # Retourner la meilleure transcription (celle avec la plus haute confiance)
        best_transcription = max(transcriptions, key=lambda x: x.get('confidence', 0))
        
        # Utiliser la langue détectée de la meilleure transcription si disponible
        # Sinon, utiliser la langue principale (Darija) par défaut
        final_detected_language = best_transcription.get('detected_language', detected_language)
        
        # Normaliser le code de langue (gérer les variantes)
        # Google peut retourner 'ar-x-maghrebi' ou d'autres variantes pour le Darija
        normalized_language = final_detected_language.lower() if final_detected_language else 'ar-ma'
        is_darija = (
            normalized_language.startswith('ar') or 
            normalized_language == 'ar-ma' or 
            'maghrebi' in normalized_language or
            'darija' in normalized_language
        )
        
        # Mapper les codes de langue pour l'affichage
        language_names = {
            'ar-MA': 'Darija (Arabe Marocain)',
            'ar': 'Darija (Arabe Marocain)',
            'ar-x-maghrebi': 'Darija (Arabe Marocain)',
            'fr-FR': 'Français',
            'fr': 'Français',
            'en-US': 'Anglais',
            'en': 'Anglais',
        }
        
        # Traduire le texte Darija en français pour la recherche
        original_text = best_transcription['text']
        translated_text = None
        translation_error = None
        
        # Si la langue détectée est Darija (toutes variantes), traduire en français
        if is_darija:
            try:
                from google.cloud import translate_v2 as translate
                from google.oauth2 import service_account
                
                # Utiliser les mêmes credentials que Speech-to-Text
                credentials_path = config('GOOGLE_APPLICATION_CREDENTIALS', default='')
                if not credentials_path and hasattr(settings, 'GOOGLE_APPLICATION_CREDENTIALS'):
                    credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS
                
                # Si le chemin n'est pas absolu, essayer de le trouver dans le dossier du projet
                if credentials_path and not os.path.isabs(credentials_path):
                    # Essayer depuis le dossier BASE_DIR
                    potential_path = os.path.join(settings.BASE_DIR, credentials_path)
                    if os.path.exists(potential_path):
                        credentials_path = potential_path
                    # Essayer aussi avec juste le nom du fichier dans BASE_DIR
                    elif os.path.exists(os.path.join(settings.BASE_DIR, os.path.basename(credentials_path))):
                        credentials_path = os.path.join(settings.BASE_DIR, os.path.basename(credentials_path))
                
                # Si toujours pas trouvé, chercher le fichier JSON dans BASE_DIR
                if not credentials_path or not os.path.exists(credentials_path):
                    # Chercher les fichiers JSON dans BASE_DIR
                    json_files = [f for f in os.listdir(settings.BASE_DIR) if f.endswith('.json') and 'aerial' in f.lower()]
                    if json_files:
                        credentials_path = os.path.join(settings.BASE_DIR, json_files[0])
                
                # Initialiser le client Translation avec les credentials explicites
                if credentials_path and os.path.exists(credentials_path):
                    # Charger les credentials depuis le fichier JSON
                    credentials = service_account.Credentials.from_service_account_file(credentials_path)
                    translate_client = translate.Client(credentials=credentials)
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(f'Translation API: Utilisation des credentials depuis {credentials_path}')
                else:
                    # Essayer avec les credentials par défaut
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f'Translation API: Credentials non trouvés. Cherché à: {credentials_path}')
                    logger.warning('Translation API: Tentative avec les credentials par défaut (GOOGLE_APPLICATION_CREDENTIALS)')
                    translate_client = translate.Client()
                
                # Traduire de l'arabe (ar) vers le français (fr)
                result = translate_client.translate(
                    original_text,
                    source_language='ar',  # Code de langue source (arabe/Darija)
                    target_language='fr'   # Code de langue cible (français)
                )
                
                translated_text = result['translatedText']
                
                # Décoder les entités HTML (comme &#39; pour ')
                import html
                translated_text = html.unescape(translated_text)
                
                # Log pour le débogage
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f'Traduction Darija → Français: "{original_text}" → "{translated_text}"')
                
            except ImportError:
                translation_error = 'Google Cloud Translation API n\'est pas installé. Installez-le avec: pip install google-cloud-translate'
            except Exception as e:
                translation_error = f'Erreur lors de la traduction: {str(e)}'
                # Log l'erreur pour le débogage
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Erreur de traduction: {translation_error}')
                # En cas d'erreur de traduction, on continue avec le texte original
        
        # Préparer la réponse
        response_data = {
            'text': original_text,  # Texte original transcrit
            'confidence': best_transcription.get('confidence', 0),
            'transcriptions': transcriptions,
            'detected_language': final_detected_language,
            'detected_language_name': language_names.get(final_detected_language, final_detected_language),
            'supported_languages': ['ar-MA', 'fr-FR', 'en-US'],
        }
        
        # Ajouter la traduction si disponible
        if translated_text:
            response_data['translated_text'] = translated_text
            response_data['search_text'] = translated_text  # Texte à utiliser pour la recherche
            response_data['translation_status'] = 'success'  # Indicateur de succès
        else:
            # Si pas de traduction, utiliser le texte original pour la recherche
            response_data['search_text'] = original_text
            response_data['translation_status'] = 'not_needed' if not is_darija else 'failed'
            if translation_error:
                response_data['translation_warning'] = translation_error
                response_data['translation_status'] = 'error'
                # Log l'erreur pour le débogage
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Erreur de traduction: {translation_error}')
        
        # Toujours inclure search_text pour que le frontend sache quoi utiliser
        # Log pour le débogage
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f'Langue détectée: {final_detected_language}, Normalisée: {normalized_language}, Est Darija: {is_darija}')
        logger.info(f'Texte original: "{original_text}", Texte de recherche: "{response_data["search_text"]}"')
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return Response({
            'error': f'Erreur lors de la transcription: {str(e)}',
            'details': error_trace if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)