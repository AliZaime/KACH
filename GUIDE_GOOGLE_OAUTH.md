# 🔐 Guide de Configuration Google OAuth

Ce guide vous explique comment configurer l'authentification Google OAuth pour votre application KACH BRIDGE AI.

## 📋 Prérequis

- Un compte Google (Gmail)
- Accès à la [Console Google Cloud](https://console.cloud.google.com/)

## 🚀 Étapes de Configuration

### 1. Créer un Projet dans Google Cloud Console

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Cliquez sur le sélecteur de projet en haut
3. Cliquez sur **"Nouveau projet"**
4. Donnez un nom à votre projet (ex: "KACH Bridge OAuth")
5. Cliquez sur **"Créer"**

### 2. Configurer l'Écran de Consentement OAuth

1. Dans le menu latéral, allez dans **"APIs & Services"** > **"OAuth consent screen"**
2. Choisissez **"External"** (ou "Internal" si vous avez un compte Google Workspace)
3. Cliquez sur **"Create"**
4. Remplissez les informations :
   - **App name**: KACH BRIDGE AI
   - **User support email**: Votre email
   - **Developer contact information**: Votre email
5. Cliquez sur **"Save and Continue"**
6. Pour les scopes, cliquez sur **"Add or Remove Scopes"**
   - Sélectionnez au minimum :
     - `.../auth/userinfo.email`
     - `.../auth/userinfo.profile`
   - Cliquez sur **"Update"** puis **"Save and Continue"**
7. Ajoutez des utilisateurs de test si nécessaire (pour le développement)
8. Cliquez sur **"Save and Continue"** puis **"Back to Dashboard"**

### 3. Créer les Identifiants OAuth 2.0

1. Allez dans **"APIs & Services"** > **"Credentials"**
2. Cliquez sur **"+ CREATE CREDENTIALS"** > **"OAuth client ID"**
3. Choisissez **"Web application"** comme type
4. Donnez un nom (ex: "KACH Bridge Web Client")
5. **Authorized JavaScript origins** :
   - Pour le développement local : `http://localhost:5173` (ou le port de Vite)
   - Pour la production : `https://votre-domaine.com`
6. **Authorized redirect URIs** :
   - Pour le développement : `http://localhost:5173` (ou le port de Vite)
   - Pour la production : `https://votre-domaine.com`
   - Note: Avec `@react-oauth/google`, les redirects sont gérés automatiquement
7. Cliquez sur **"Create"**
8. **Copiez le Client ID** (vous en aurez besoin pour le frontend)

### 4. Configuration Backend (Django)

Le backend est déjà configuré pour accepter les tokens Google. Aucune configuration supplémentaire n'est nécessaire côté backend.

### 5. Configuration Frontend (React)

#### 5.1. Installer la dépendance

```bash
cd Kachbridgeai
npm install @react-oauth/google
```

#### 5.2. Configurer les variables d'environnement

Créez un fichier `.env` dans le dossier `Kachbridgeai/` :

```env
VITE_GOOGLE_CLIENT_ID=votre-client-id-google.apps.googleusercontent.com
VITE_API_BASE_URL=http://localhost:8000
```

**Important** : Remplacez `votre-client-id-google.apps.googleusercontent.com` par le Client ID que vous avez copié à l'étape 3.

#### 5.3. Vérifier la configuration

Le code est déjà en place :
- ✅ `main.tsx` : GoogleOAuthProvider configuré
- ✅ `Login.tsx` : Bouton Google ajouté
- ✅ `AuthContext.tsx` : Méthode `loginWithGoogle` ajoutée
- ✅ `api.ts` : Endpoint Google configuré

### 6. Créer la Migration de Base de Données

Exécutez la migration pour ajouter le champ `google_id` au modèle User :

```bash
cd KACH
python manage.py makemigrations
python manage.py migrate
```

### 7. Installer les Dépendances Backend

```bash
cd KACH
pip install -r requirements.txt
```

## 🧪 Tester la Connexion Google

1. Démarrez le backend Django :
   ```bash
   cd KACH
   python manage.py runserver
   ```

2. Démarrez le frontend React :
   ```bash
   cd Kachbridgeai
   npm run dev
   ```

3. Ouvrez votre navigateur sur `http://localhost:5173` (ou le port affiché)
4. Cliquez sur **"Se connecter"**
5. Cliquez sur le bouton **"Se connecter avec Google"**
6. Sélectionnez votre compte Google
7. Autorisez l'application
8. Vous devriez être connecté automatiquement !

## 🔒 Sécurité en Production

### Variables d'Environnement

**Backend** : Créez un fichier `.env` dans `KACH/` :

```env
SECRET_KEY=votre-secret-key-django
DEBUG=False
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com
CORS_ALLOWED_ORIGINS=https://votre-domaine.com
```

**Frontend** : Utilisez les variables d'environnement de votre plateforme de déploiement (Vercel, Netlify, etc.)

### Configuration Google Cloud pour Production

1. Dans Google Cloud Console, ajoutez votre domaine de production :
   - **Authorized JavaScript origins** : `https://votre-domaine.com`
   - **Authorized redirect URIs** : `https://votre-domaine.com`

2. Publiez votre application OAuth (si vous êtes prêt) :
   - Allez dans **"OAuth consent screen"**
   - Cliquez sur **"PUBLISH APP"**

## 🐛 Dépannage

### Erreur : "Invalid client ID"

- Vérifiez que `VITE_GOOGLE_CLIENT_ID` est correctement défini dans `.env`
- Redémarrez le serveur de développement après avoir modifié `.env`

### Erreur : "Redirect URI mismatch"

- Vérifiez que l'URL dans **Authorized JavaScript origins** correspond à votre URL de développement/production
- Pour le développement local, utilisez `http://localhost:5173` (ou votre port Vite)

### Erreur : "Token Google invalide"

- Vérifiez que le backend Django est démarré
- Vérifiez que les CORS sont correctement configurés dans `settings.py`
- Vérifiez les logs du backend pour plus de détails

### L'utilisateur n'est pas créé

- Vérifiez que la migration a été exécutée : `python manage.py migrate`
- Vérifiez les logs du backend Django

## 📚 Ressources

- [Documentation Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
- [Documentation @react-oauth/google](https://www.npmjs.com/package/@react-oauth/google)
- [Google Cloud Console](https://console.cloud.google.com/)

## ✅ Checklist de Configuration

- [ ] Projet créé dans Google Cloud Console
- [ ] Écran de consentement OAuth configuré
- [ ] Client ID OAuth créé
- [ ] Client ID ajouté dans `.env` du frontend
- [ ] Migration de base de données exécutée
- [ ] Dépendances installées (backend et frontend)
- [ ] Test de connexion Google réussi
- [ ] Configuration de production effectuée (si applicable)

---

**Note** : Pour une version pro, vous pouvez également ajouter :
- Connexion avec Facebook, GitHub, etc.
- Gestion des rôles utilisateurs (Premium, Pro, etc.)
- Abonnements et facturation
- Analytics et tracking

Bon développement ! 🚀

