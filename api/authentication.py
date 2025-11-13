"""
Authentification personnalisée pour vérifier la blacklist des access tokens
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
import jwt
from django.conf import settings


class JWTAuthenticationWithBlacklist(JWTAuthentication):
    """
    Authentification JWT qui vérifie aussi la blacklist pour les access tokens
    """
    
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        
        # Vérifier si le token est blacklisté
        try:
            # Décoder le token pour obtenir le jti
            raw_token_str = str(validated_token)
            decoded_token = jwt.decode(
                raw_token_str,
                settings.SECRET_KEY,
                algorithms=['HS256'],
                options={"verify_signature": False}  # On vérifie juste pour obtenir le jti
            )
            jti = decoded_token.get('jti')
            
            if jti:
                # Vérifier si ce token est dans la blacklist
                outstanding_token = OutstandingToken.objects.filter(jti=jti).first()
                if outstanding_token:
                    if BlacklistedToken.objects.filter(token=outstanding_token).exists():
                        raise InvalidToken('Token has been blacklisted.')
            else:
                # Si pas de jti, vérifier par le token string directement
                outstanding_token = OutstandingToken.objects.filter(token=raw_token_str).first()
                if outstanding_token:
                    if BlacklistedToken.objects.filter(token=outstanding_token).exists():
                        raise InvalidToken('Token has been blacklisted.')
        except InvalidToken:
            # Re-raise les erreurs de blacklist
            raise
        except (jwt.InvalidTokenError, TokenError, Exception):
            # Si on ne peut pas décoder ou vérifier, on laisse passer
            # (l'authentification de base gérera l'erreur)
            pass
        
        return self.get_user(validated_token), validated_token

