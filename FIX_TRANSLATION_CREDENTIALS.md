# Correction du problème de credentials pour la traduction

Si vous voyez l'erreur "Your default credentials were not found" lors de la traduction Darija → Français, suivez ces étapes :

## Solution rapide

### Option 1 : Définir la variable d'environnement (Recommandé)

**Windows (PowerShell):**
```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\Users\aliza\OneDrive\Desktop\KACH BRIDGE AI\KACH\aerial-grid-478010-p6-310bff494c47.json"
```

**Windows (CMD):**
```cmd
set GOOGLE_APPLICATION_CREDENTIALS=C:\Users\aliza\OneDrive\Desktop\KACH BRIDGE AI\KACH\aerial-grid-478010-p6-310bff494c47.json
```

**Linux/Mac:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/chemin/vers/KACH/aerial-grid-478010-p6-310bff494c47.json"
```

### Option 2 : Utiliser un fichier .env

Créez un fichier `.env` dans le dossier `KACH/` avec :

```
GOOGLE_APPLICATION_CREDENTIALS=./aerial-grid-478010-p6-310bff494c47.json
```

### Option 3 : Le code cherche automatiquement

Le code a été amélioré pour chercher automatiquement le fichier JSON dans le dossier du projet. Si le fichier `aerial-grid-478010-p6-310bff494c47.json` est dans le dossier `KACH/`, il devrait être trouvé automatiquement.

## Vérification

1. Redémarrez votre serveur Django après avoir défini la variable d'environnement
2. Testez à nouveau la transcription audio en Darija
3. Vérifiez les logs du serveur Django pour voir si les credentials sont bien chargés

## Logs à vérifier

Dans les logs du serveur Django, vous devriez voir :
```
Translation API: Utilisation des credentials depuis /chemin/vers/fichier.json
```

Si vous voyez un avertissement, cela signifie que les credentials n'ont pas été trouvés.

## Activer l'API Translation

Assurez-vous que l'API Cloud Translation API est activée dans votre projet Google Cloud :

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. APIs & Services > Library
3. Recherchez "Cloud Translation API"
4. Cliquez sur "Enable"

## Permissions du compte de service

Vérifiez que votre compte de service a les permissions nécessaires :
- Cloud Speech-to-Text API User
- Cloud Translation API User

