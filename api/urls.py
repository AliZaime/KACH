from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentification
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('auth/google/', views.google_oauth, name='google_oauth'),
    path('auth/logout/', views.logout_user, name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profil utilisateur
    path('user/profile/', views.get_user_profile, name='user_profile'),
    path('user/profile/update/', views.update_user_profile, name='update_user_profile'),
    path('user/profile/change-password/', views.change_password, name='change_password'),
    
    # Health check
    path('health/', views.health_check, name='health_check'),
    
    # Speech-to-Text
    path('speech/transcribe/', views.transcribe_audio, name='transcribe_audio'),
    
    # Endpoint de recherche
    path('api/search/', views.search_products),
]

