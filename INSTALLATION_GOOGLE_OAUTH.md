# 🚀 Installation Rapide - Google OAuth

## Étapes d'Installation

### 1. Backend (Django)

```bash
cd KACH

# Installer les dépendances
pip install -r requirements.txt

# Créer et appliquer la migration pour ajouter google_id
python manage.py makemigrations
python manage.py migrate
```

### 2. Frontend (React)

```bash
cd Kachbridgeai

# Installer les dépendances
npm install @react-oauth/google

# Créer le fichier .env avec votre Client ID Google
# Voir GUIDE_GOOGLE_OAUTH.md pour obtenir le Client ID
echo "VITE_GOOGLE_CLIENT_ID=votre-client-id-google.apps.googleusercontent.com" > .env
echo "VITE_API_BASE_URL=http://localhost:8000" >> .env
```

### 3. Démarrer les Serveurs

**Terminal 1 - Backend:**
```bash
cd KACH
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd Kachbridgeai
npm run dev
```

### 4. Tester

1. Ouvrez `http://localhost:5173` (ou le port affiché)
2. Cliquez sur "Se connecter"
3. Cliquez sur "Se connecter avec Google"
4. Sélectionnez votre compte Google

## ⚠️ Important

Avant de tester, vous devez :
1. Créer un projet dans Google Cloud Console
2. Configurer OAuth 2.0
3. Obtenir votre Client ID
4. Ajouter le Client ID dans `.env`

**Voir `GUIDE_GOOGLE_OAUTH.md` pour les détails complets.**

