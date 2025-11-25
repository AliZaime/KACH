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

## 🔑 Configuration Google Cloud API - Télécharger la clé JSON

Si vous avez besoin de télécharger ou re-télécharger la clé JSON de votre compte de service Google Cloud, suivez ces étapes :

### Méthode 1 : Télécharger une clé existante

1. **Accéder à Google Cloud Console**
   - Allez sur [Google Cloud Console](https://console.cloud.google.com/)
   - Connectez-vous avec votre compte Google

2. **Sélectionner le projet**
   - Dans le menu déroulant en haut, sélectionnez votre projet

3. **Accéder aux comptes de service**
   - Allez dans **IAM & Admin** > **Service Accounts** (Comptes de service)
   - Ou utilisez ce lien direct : `https://console.cloud.google.com/iam-admin/serviceaccounts`

4. **Trouver votre compte de service**
   - Cliquez sur le compte de service que vous souhaitez utiliser
   - Si vous n'en avez pas, créez-en un nouveau (voir Méthode 2)

5. **Télécharger la clé JSON**
   - Dans l'onglet **KEYS** (Clés)
   - Cliquez sur **ADD KEY** > **Create new key** (Créer une nouvelle clé)
   - Sélectionnez le format **JSON**
   - Cliquez sur **CREATE** (Créer)
   - Le fichier JSON sera téléchargé automatiquement

6. **Sauvegarder la clé**
   - Placez le fichier JSON dans le dossier `KACH/`
   - **⚠️ IMPORTANT** : Ne commitez jamais ce fichier dans Git (il est déjà dans `.gitignore`)
   - Renommez-le si nécessaire (ex: `google-credentials.json`)

### Méthode 2 : Créer un nouveau compte de service

Si vous n'avez pas encore de compte de service :

1. **Créer un compte de service**
   - Dans **IAM & Admin** > **Service Accounts**
   - Cliquez sur **CREATE SERVICE ACCOUNT** (Créer un compte de service)
   - Remplissez les informations :
     - **Service account name** : Nom de votre choix
     - **Service account ID** : Généré automatiquement
     - **Description** : Description optionnelle
   - Cliquez sur **CREATE AND CONTINUE**

2. **Attribuer les rôles** (optionnel)
   - Ajoutez les rôles nécessaires (ex: Cloud Storage Admin, etc.)
   - Cliquez sur **CONTINUE** puis **DONE**

3. **Télécharger la clé JSON**
   - Cliquez sur le compte de service créé
   - Allez dans l'onglet **KEYS**
   - Cliquez sur **ADD KEY** > **Create new key**
   - Sélectionnez **JSON** et cliquez sur **CREATE**
   - Le fichier sera téléchargé

### Configuration dans votre application

Après avoir téléchargé la clé JSON :

1. **Placer le fichier**
   ```bash
   # Placez le fichier dans le dossier KACH/
   KACH/google-credentials.json
   ```

2. **Configurer dans .env** (si nécessaire)
   ```env
   GOOGLE_APPLICATION_CREDENTIALS=google-credentials.json
   ```

3. **Ou utiliser directement dans le code**
   ```python
   import os
   from google.oauth2 import service_account
   
   credentials = service_account.Credentials.from_service_account_file(
       'google-credentials.json'
   )
   ```

### ⚠️ Sécurité importante

- **Ne jamais** commiter le fichier JSON dans Git
- **Ne jamais** partager publiquement votre clé JSON
- Si une clé est compromise, supprimez-la immédiatement dans Google Cloud Console
- Utilisez des variables d'environnement pour les chemins de fichiers sensibles

### 🔗 Liens utiles

- [Google Cloud Console](https://console.cloud.google.com/)
- [Documentation Service Accounts](https://cloud.google.com/iam/docs/service-accounts)
- [Guide d'authentification Google](https://cloud.google.com/docs/authentication)

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

