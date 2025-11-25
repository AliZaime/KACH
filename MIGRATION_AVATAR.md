# Migration pour ajouter le champ avatar

Après avoir ajouté le champ `avatar` au modèle `User`, vous devez créer et appliquer une migration.

## Étapes

1. **Créer la migration** :
```bash
cd KACH
python manage.py makemigrations
```

2. **Appliquer la migration** :
```bash
python manage.py migrate
```

3. **Vérifier que tout fonctionne** :
```bash
python manage.py runserver
```

## Notes

- Le champ `avatar` est optionnel (null=True, blank=True)
- Les images seront stockées dans le dossier `media/avatars/`
- Assurez-vous que le dossier `media` existe et est accessible
- En production, configurez le serveur web pour servir les fichiers média

