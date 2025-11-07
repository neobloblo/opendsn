# Guide Git - OpenDSN v2.0.0

## 📋 Résumé des modifications

### Fichiers modifiés (6)
1. `README.md` - Documentation mise à jour
2. `app.py` - Nouvelle route /categories-socioprofessionnelles + modifications terminologie
3. `dsn.db` - Table nomenclature_pcs_ese ajoutée
4. `dsn_parser.py` - Fonctions nomenclature + distinction Groupe/CSP
5. `templates/base.html` - Nouveau lien navigation
6. `templates/evolution_effectif.html` - Graphiques Groupe + Tableau récapitulatif

### Nouveaux fichiers (4)
1. `CHANGELOG.md` - Historique des modifications
2. `import_nomenclature.py` - Script d'import nomenclature
3. `nomenclature_pcs_ese.sql` - 412 codes PCS-ESE
4. `templates/categories_socioprofessionnelles.html` - Nouvelle page

## 🚀 Commandes Git à exécuter

### Étape 1 : Vérifier l'état actuel
```bash
cd opendsn2
git status
```

### Étape 2 : Ajouter tous les fichiers modifiés et nouveaux
```bash
git add .
```

### Étape 3 : Créer le commit
```bash
git commit -m "feat: v2.0.0 - Nomenclature PCS-ESE complète et distinction Groupe/CSP

- Ajout de la nomenclature PCS-ESE complète (412 codes)
- Nouvelle page 'Catégories Socioprofessionnelles'
- Correction terminologique : distinction Groupe (1er chiffre) / CSP (2 chiffres)
- Récapitulatif détaillé par salarié avec sélecteur de période
- Graphiques par Groupe CSP (camembert + courbes)
- Libellés emploi récupérés automatiquement depuis la nomenclature
- Script d'import nomenclature (import_nomenclature.py)
- Documentation complète (README.md, CHANGELOG.md)

BREAKING CHANGE: Renommage de toutes les variables 'csp' en 'groupe' dans le code
pour respecter la nomenclature officielle PCS-ESE de l'INSEE.

Closes #X (remplacer X par le numéro d'issue si applicable)
"
```

### Étape 4 : Pousser vers le dépôt distant
```bash
git push origin master
```

## 📝 Message de commit détaillé

Le message de commit suit la convention [Conventional Commits](https://www.conventionalcommits.org/) :

**Format** : `<type>(<portée>): <sujet>`

**Type** : `feat` (nouvelle fonctionnalité)

**Breaking Change** : Indiqué car modification importante de la terminologie

**Corps du message** :
- Liste les ajouts principaux
- Liste les modifications importantes
- Mentionne les fichiers clés

## 🏷️ Optionnel : Créer un tag de version

Si vous voulez marquer cette version :

```bash
# Créer un tag annoté
git tag -a v2.0.0 -m "Version 2.0.0 - Nomenclature PCS-ESE complète

Ajouts majeurs:
- Nomenclature PCS-ESE intégrée (412 codes)
- Page Catégories Socioprofessionnelles
- Distinction Groupe/CSP
- Récapitulatif détaillé par salarié
- Graphiques par Groupe CSP

Voir CHANGELOG.md pour tous les détails."

# Pousser le tag
git push origin v2.0.0

# Ou pousser tous les tags
git push --tags
```

## 🔍 Vérifications avant le push

### 1. Vérifier les fichiers à commiter
```bash
git status
```

### 2. Vérifier le diff
```bash
# Voir tous les changements
git diff

# Voir les changements staged
git diff --staged
```

### 3. Vérifier l'historique
```bash
# Voir les derniers commits
git log --oneline -5

# Voir le commit en détail
git show HEAD
```

## 📚 Après le push

### Créer une Pull Request (si workflow PR)
1. Aller sur GitHub : https://github.com/neobloblo/opendsn
2. Cliquer sur "Pull requests" → "New pull request"
3. Sélectionner votre branche
4. Ajouter un titre et description
5. Référencer le CHANGELOG.md

### Créer une Release sur GitHub (recommandé)
1. Aller sur GitHub → Releases
2. Cliquer sur "Draft a new release"
3. **Tag version** : `v2.0.0`
4. **Release title** : `v2.0.0 - Nomenclature PCS-ESE complète`
5. **Description** : Copier le contenu pertinent du CHANGELOG.md
6. Cocher "Set as the latest release"
7. Publier

## ⚠️ Notes importantes

### Base de données (dsn.db)
La base de données est modifiée car elle contient maintenant la table `nomenclature_pcs_ese`.
Si vous ne voulez pas versionner la DB, décommentez `dsn.db` dans `.gitignore`.

### Fichiers sensibles
Vérifiez qu'aucun fichier sensible n'est commité :
```bash
# Vérifier les fichiers ignorés
git status --ignored

# Vérifier qu'il n'y a pas de fichiers .env
git ls-files | grep .env
```

### Taille du commit
Ce commit est conséquent (nouvelle nomenclature SQL de 412 lignes). C'est normal.

## 🔄 Si vous devez annuler

### Avant le commit
```bash
# Retirer tous les fichiers du staging
git reset

# Retirer un fichier spécifique
git reset HEAD <fichier>

# Annuler les modifications d'un fichier
git restore <fichier>
```

### Après le commit mais avant le push
```bash
# Modifier le dernier commit
git commit --amend

# Annuler le dernier commit (garde les modifications)
git reset --soft HEAD~1

# Annuler le dernier commit (supprime les modifications)
git reset --hard HEAD~1
```

### Après le push
```bash
# Créer un commit qui annule les changements
git revert HEAD

# Forcer le push (ATTENTION : à éviter si d'autres collaborent)
git push --force origin master
```

## 📞 Support

Si vous rencontrez des problèmes :
1. Consultez la [documentation Git](https://git-scm.com/doc)
2. Vérifiez le fichier [DEPLOIEMENT.md](DEPLOIEMENT.md)
3. Ouvrez une issue sur GitHub

---

**Date de préparation** : 2025-11-07
**Version préparée** : 2.0.0
**Branche actuelle** : master
**Commits en avance** : 2 commits
