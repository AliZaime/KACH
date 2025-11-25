# Configuration Google Cloud Speech-to-Text et Translation pour le Darija

Ce guide explique comment configurer Google Cloud Speech-to-Text et Translation API pour la transcription et la traduction automatique de l'arabe marocain (Darija) vers le français dans votre application.

## Prérequis

1. Un compte Google Cloud Platform (GCP)
2. Un projet GCP avec l'API Speech-to-Text activée
3. Un fichier de credentials JSON pour l'authentification

## Étapes de configuration

### 1. Créer un projet Google Cloud

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet ou sélectionnez un projet existant
3. Notez le nom de votre projet

### 2. Activer les APIs nécessaires

1. Dans la console GCP, allez dans **APIs & Services** > **Library**
2. Recherchez et activez les APIs suivantes :
   - **Cloud Speech-to-Text API** - Pour la transcription audio
   - **Cloud Translation API** - Pour la traduction Darija → Français
3. Cliquez sur **Enable** pour chaque API

### 3. Créer un compte de service

1. Allez dans **APIs & Services** > **Credentials**
2. Cliquez sur **Create Credentials** > **Service Account**
3. Donnez un nom à votre compte de service (ex: `speech-to-text-service`)
4. Cliquez sur **Create and Continue**
5. Attribuez le rôle **Cloud Speech-to-Text API User** ou **Editor**
6. Cliquez sur **Done**

### 4. Générer une clé JSON

1. Dans la liste des comptes de service, cliquez sur celui que vous venez de créer
2. Allez dans l'onglet **Keys**
3. Cliquez sur **Add Key** > **Create new key**
4. Sélectionnez **JSON**
5. Cliquez sur **Create** - le fichier JSON sera téléchargé automatiquement

**Important** : Assurez-vous que le compte de service a les permissions pour :
- **Cloud Speech-to-Text API User** (ou **Editor**)
- **Cloud Translation API User** (ou **Editor**)

### 5. Configurer les credentials dans votre projet

Vous avez deux options pour configurer les credentials :

#### Option A : Variable d'environnement (Recommandé)

1. Placez le fichier JSON dans le dossier `KACH/` (ex: `aerial-grid-478010-p6-310bff494c47.json`)
2. Définissez la variable d'environnement :

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
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
```

#### Option B : Fichier .env

1. Créez un fichier `.env` dans le dossier `KACH/`
2. Ajoutez la ligne suivante :
```
GOOGLE_APPLICATION_CREDENTIALS=./aerial-grid-478010-p6-310bff494c47.json
```

### 6. Installer les dépendances

Dans le dossier `KACH/`, installez les bibliothèques Google Cloud nécessaires :

```bash
pip install google-cloud-speech>=2.21.0
pip install google-cloud-translate>=3.15.0
```

Ou si vous utilisez un environnement virtuel :

```bash
# Activez votre environnement virtuel
.\venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac

# Installez les dépendances
pip install -r requirements.txt
```

Les dépendances incluent maintenant :
- `google-cloud-speech` : Pour la transcription audio
- `google-cloud-translate` : Pour la traduction Darija → Français

## Configuration des langues et traduction automatique

Le système est configuré pour reconnaître **plusieurs langues** avec les priorités suivantes :

1. **Darija (ar-MA)** - Langue principale : Arabe marocain
2. **Français (fr-FR)** - Langue secondaire
3. **Anglais (en-US)** - Langue tertiaire

Google Cloud Speech-to-Text détecte automatiquement la langue parlée parmi ces trois options et retourne la transcription avec la langue détectée.

### Traduction automatique Darija → Français

**Fonctionnalité importante** : Si le système détecte que l'utilisateur parle en **Darija**, le texte est automatiquement traduit en **français** pour être utilisé comme mot-clé de recherche.

- **Texte original** : Affiché dans l'interface (Darija)
- **Texte traduit** : Généré automatiquement en français
- **Recherche** : Utilise le texte français traduit pour de meilleurs résultats

Cette fonctionnalité permet aux utilisateurs de rechercher en parlant en Darija tout en utilisant des mots-clés en français pour la recherche.

### Modifier les langues

Si vous souhaitez modifier les langues supportées, éditez `KACH/api/views.py` lignes 448-451 :

```python
'language_code': 'ar-MA',  # Langue principale
'alternative_language_codes': ['fr-FR', 'en-US'],  # Langues secondaires
```

### Modèles disponibles

- `latest_long` : Modèle actuel, optimisé pour les enregistrements longs
- `phone_call` : Alternative pour les conversations téléphoniques

## Test de l'API

Une fois configuré, vous pouvez tester l'endpoint :

```bash
curl -X POST http://localhost:8000/api/speech/transcribe/ \
  -F "audio=@votre_fichier_audio.webm"
```

## Support des langues

Le système supporte actuellement **3 langues** avec détection automatique :

- **ar-MA** : Arabe marocain (Darija) - **Langue principale**
- **fr-FR** : Français - Langue secondaire
- **en-US** : Anglais - Langue tertiaire

La langue est détectée automatiquement et affichée dans l'interface utilisateur avec la transcription.

## Coûts

### Speech-to-Text API
- **Audio standard** : $0.006 par 15 secondes
- **Audio amélioré** : $0.009 par 15 secondes (avec le modèle `latest_long`)

### Translation API
- **Traduction** : $20 par million de caractères traduits
- Les 500 000 premiers caractères par mois sont **gratuits**

**Note** : La traduction n'est effectuée que si le Darija est détecté, ce qui limite les coûts.

Consultez les pages de tarification pour plus de détails :
- [Speech-to-Text Pricing](https://cloud.google.com/speech-to-text/pricing)
- [Translation API Pricing](https://cloud.google.com/translate/pricing)

## Dépannage

### Erreur : "GOOGLE_APPLICATION_CREDENTIALS not found"
- Vérifiez que la variable d'environnement est bien définie
- Vérifiez que le chemin vers le fichier JSON est correct
- Vérifiez que le fichier JSON existe et est lisible

### Erreur : "Permission denied"
- Vérifiez que le compte de service a le rôle approprié
- Vérifiez que l'API Speech-to-Text est activée dans votre projet

### Transcription vide ou incorrecte
- Vérifiez que l'audio est clair et sans trop de bruit de fond
- Essayez avec le code de langue `ar` au lieu de `ar-MA`
- Vérifiez que le format audio est supporté (WEBM_OPUS, WAV, MP3, FLAC)

## Sécurité

⚠️ **Important** : Ne commitez jamais votre fichier de credentials JSON dans Git !

Ajoutez-le à votre `.gitignore` :
```
*.json
!package.json
!package-lock.json
```

Ou spécifiquement :
```
aerial-grid-*.json
GOOGLE_APPLICATION_CREDENTIALS.json
```

