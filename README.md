# KACH-BRIDGE - Backend Multiplateforme Django

Backend API REST développé avec Django et Django REST Framework, conçu pour fonctionner avec des applications web et mobiles.

## 🚀 Fonctionnalités

- ✅ API REST avec Django REST Framework
- ✅ Authentification JWT (JSON Web Tokens)
- ✅ Support CORS pour les applications web et mobiles
- ✅ Modèle utilisateur personnalisé
- ✅ Endpoints d'authentification (inscription, connexion, déconnexion)
- ✅ Gestion de profil utilisateur
- ✅ Configuration sécurisée et prête pour la production

## 📋 Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- virtualenv (recommandé)

## 🛠️ Installation

### 1. Cloner le projet (si applicable)

```bash
cd KACH-BRIDGE
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
```

### 3. Activer l'environnement virtuel

**Sur Windows:**
```bash
venv\Scripts\activate
```

**Sur Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 5. Configurer les variables d'environnement

Copiez le fichier `.env.example` vers `.env` et modifiez les valeurs selon vos besoins:

```bash
copy .env.example .env  # Windows
# ou
cp .env.example .env    # Linux/Mac
```

### 6. Effectuer les migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Créer un superutilisateur (optionnel)

```bash
python manage.py createsuperuser
```

### 8. Lancer le serveur de développement

```bash
python manage.py runserver
```

Le serveur sera accessible sur `http://localhost:8000`

## 📡 Endpoints API

### Authentification

- `POST /api/auth/register/` - Inscription d'un nouvel utilisateur
- `POST /api/auth/login/` - Connexion d'un utilisateur
- `POST /api/auth/logout/` - Déconnexion (nécessite un token)
- `POST /api/auth/token/refresh/` - Rafraîchir le token d'accès

### Utilisateur

- `GET /api/user/profile/` - Récupérer le profil de l'utilisateur connecté (nécessite authentification)

### Utilitaires

- `GET /api/health/` - Vérification de santé de l'API

## 🔐 Authentification

L'API utilise JWT (JSON Web Tokens) pour l'authentification. 

### Exemple d'utilisation

**Inscription:**
```bash
POST /api/auth/register/
{
  "username": "alizaime",
  "email": "ali@example.com",
  "password": "motdepasse123",
  "password_confirm": "motdepasse123",
  "first_name": "Ali",
  "last_name": "ZAIME"
}
```

**Connexion:**
```bash
POST /api/auth/login/
{
  "username": "alizaime",
  "password": "motdepasse123"
}
```

**Réponse:**
```json
{
  "user": {
    "id": 1,
    "username": "alizaime",
    "email": "ali@example.com",
    ...
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**Utiliser le token:**
Ajoutez le header suivant à vos requêtes:
```
Authorization: Bearer <access_token>
```

## 🌐 Configuration CORS

Le backend est configuré pour accepter les requêtes depuis différentes origines. Modifiez `CORS_ALLOWED_ORIGINS` dans votre fichier `.env` pour ajouter les URLs de vos applications frontend.

## 📁 Structure du projet

```
KACH-BRIDGE/
├── api/                    # Application API principale
│   ├── models.py          # Modèles de données
│   ├── serializers.py     # Serializers DRF
│   ├── views.py           # Vues API
│   └── urls.py            # URLs de l'API
├── kach_bridge/           # Configuration du projet Django
│   ├── settings.py        # Paramètres Django
│   ├── urls.py            # URLs principales
│   └── wsgi.py            # Configuration WSGI
├── manage.py              # Script de gestion Django
├── requirements.txt       # Dépendances Python
└── README.md             # Ce fichier
```

## 🔒 Sécurité

- Les mots de passe sont hashés automatiquement par Django
- JWT avec rotation des tokens de rafraîchissement
- CORS configuré de manière sécurisée
- Validation des données avec les serializers DRF

## 📝 Prochaines étapes

- Ajouter des endpoints spécifiques à votre domaine métier
- Implémenter la gestion des permissions avancées
- Ajouter des tests unitaires et d'intégration
- Configurer la base de données de production (PostgreSQL, MySQL, etc.)
- Mettre en place la documentation API avec Swagger/OpenAPI

## 👨‍💻 Développeur

Ali ZAIME

## 📄 Licence

Ce projet est privé.

