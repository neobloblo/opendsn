# 📘 Guide de Reprise du Projet OpenDSN

**Version actuelle** : 2.0.0
**Date** : 2025-11-07
**Statut** : ✅ Prêt pour commit Git

## 🎯 Objectif du projet

OpenDSN est une application web Flask pour analyser les fichiers DSN (Déclaration Sociale Nominative) et calculer automatiquement l'Index Égalité Professionnelle Femmes-Hommes selon la réglementation française.

## 📂 Structure du projet

```
opendsn2/
├── 📄 app.py                                   # Application Flask principale
├── 📄 dsn_parser.py                            # Parser DSN avec nomenclature PCS-ESE
├── 📄 import_nomenclature.py                   # Script d'import nomenclature
├── 📄 requirements.txt                         # Dépendances Python
├── 📄 Procfile                                 # Config Railway/Heroku
├── 📄 runtime.txt                              # Python 3.11
├── 📄 dsn.db                                   # SQLite (structures + nomenclature)
├── 📄 nomenclature_pcs_ese.sql                 # 412 codes PCS-ESE
│
├── 📁 templates/
│   ├── base.html                               # Template de base
│   ├── accueil.html                            # Page d'accueil
│   ├── structures.html                         # Structures DSN
│   ├── rubriques.html                          # Rubriques DSN
│   ├── categories_socioprofessionnelles.html   # ⭐ NOUVEAU
│   ├── egalite_hf.html                         # Index Égalité
│   └── evolution_effectif.html                 # Évolution effectif
│
├── 📁 uploads/                                 # Fichiers DSN uploadés
├── 📁 venv/                                    # Environnement virtuel
│
├── 📄 README.md                                # Documentation principale
├── 📄 CHANGELOG.md                             # ⭐ NOUVEAU - Historique
├── 📄 GIT_GUIDE.md                             # ⭐ NOUVEAU - Guide Git
├── 📄 REPRISE_PROJET.md                        # ⭐ NOUVEAU - Ce fichier
├── 📄 DEPLOIEMENT.md                           # Guide déploiement
├── 📄 NOTES.md                                 # Notes diverses
└── 📄 .gitignore                               # Fichiers ignorés
```

## 🚀 Démarrage rapide

### 1. Cloner et configurer

```bash
cd D:\ClaudeProjects\opendsn2

# Activer l'environnement virtuel
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac

# Vérifier les dépendances
pip install -r requirements.txt
```

### 2. Importer la nomenclature (si nécessaire)

```bash
python import_nomenclature.py
```

Sortie attendue :
```
Connexion à la base de données : D:\ClaudeProjects\opendsn2\dsn.db
Suppression de la table existante si presente...
Lecture du fichier SQL : D:\ClaudeProjects\opendsn2\nomenclature_pcs_ese.sql
Execution du script SQL...
OK - 412 codes PCS-ESE importes avec succes !

Quelques exemples de codes importes :
  21       : Agriculteurs sur petite exploitation
  22       : Agriculteurs sur moyenne exploitation
  23       : Agriculteurs sur grande exploitation
  ...
```

### 3. Lancer l'application

```bash
python app.py
```

L'application sera accessible sur : **http://localhost:8050**

## 🆕 Nouveautés de la version 2.0.0

### 1. Nomenclature PCS-ESE complète
- **412 codes** PCS-ESE intégrés dans la base de données
- Libellés d'emploi récupérés automatiquement
- Fichier source : `nomenclature_pcs_ese.sql`
- Script d'import : `import_nomenclature.py`

### 2. Nouvelle page : Catégories Socioprofessionnelles
- **URL** : http://localhost:8050/categories-socioprofessionnelles
- **Contenu** :
  - Les 5 groupes de CSP
  - Les CSP détaillées (2 chiffres)
  - Nomenclature complète organisée par groupe
  - Documentation d'utilisation

### 3. Distinction Groupe / CSP
**Changement terminologique majeur** :

| Avant | Maintenant |
|-------|------------|
| CSP = 1er chiffre | **Groupe** = 1er chiffre (2-6) |
| - | **CSP** = 2 premiers chiffres |

**Codes internes (Index Égalité)** :
- 21 = Ouvriers
- 22 = Employés
- 23 = Agents de maîtrise
- 24 = Cadres
- 25 = Cadres dirigeants
- 26 = Autres

### 4. Récapitulatif par salarié (Évolution de l'effectif)
- Sélecteur de période
- 14 colonnes d'informations
- Groupe, CSP et libellé emploi affichés
- Statut avec badges colorés

### 5. Graphiques par Groupe CSP
- Graphique en camembert (répartition)
- Graphique en courbes (évolution)

## 🔧 Points techniques importants

### Parser DSN (`dsn_parser.py`)

**Nouvelles fonctions** :
```python
_determine_groupe_from_pcs_ese(code)  # Extrait le groupe (1er chiffre)
_extract_csp_from_pcs_ese(code)       # Extrait la CSP (2 chiffres)
get_libelle_csp(csp_code)             # Récupère le libellé CSP
get_libelle_emploi(code_pcs_ese)      # Récupère le libellé emploi
_load_nomenclature_pcs_ese()          # Charge la nomenclature (avec cache)
_groupe_to_code(groupe)               # Convertit groupe → code interne
```

**Cache nomenclature** :
```python
class DSNParser:
    _nomenclature_pcs_ese = None  # Cache classe
```

### Base de données (`dsn.db`)

**Nouvelle table** :
```sql
CREATE TABLE nomenclature_pcs_ese (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,           -- Ex: "382a", "524a"
    libelle TEXT NOT NULL,                -- Ex: "Ingénieurs et cadres..."
    categorie_principale INTEGER          -- 1-6 (groupe)
);
```

**Vérifier les données** :
```bash
sqlite3 dsn.db
SELECT COUNT(*) FROM nomenclature_pcs_ese;  -- Doit retourner 412
SELECT * FROM nomenclature_pcs_ese LIMIT 5;
.quit
```

### Routes Flask (`app.py`)

**Routes disponibles** :
- `/` - Accueil
- `/structures` - Structures DSN
- `/rubriques` - Rubriques DSN
- `/categories-socioprofessionnelles` - ⭐ NOUVEAU
- `/egalite-hf` - Index Égalité
- `/evolution-effectif` - Évolution effectif
- `/analyse` - Analyse

## 📊 Utilisation de l'application

### 1. Index Égalité Professionnelle
1. Accéder à http://localhost:8050/egalite-hf
2. Uploader 1-12 fichiers DSN mensuels
3. Sélectionner types de rémunération
4. Consulter les 5 indicateurs

### 2. Évolution de l'effectif
1. Accéder à http://localhost:8050/evolution-effectif
2. Uploader 1-24 fichiers DSN mensuels
3. Consulter :
   - Statistiques globales
   - Graphiques d'évolution
   - Graphiques par Groupe CSP ⭐
   - Récapitulatif par salarié ⭐

### 3. Catégories Socioprofessionnelles ⭐
1. Accéder à http://localhost:8050/categories-socioprofessionnelles
2. Explorer :
   - Les 5 groupes
   - Les CSP (2 chiffres)
   - La nomenclature complète (412 codes)

## 🐛 Problèmes courants et solutions

### Import nomenclature échoue
**Problème** : Erreur Unicode lors de l'import
**Solution** : Le script utilise déjà `encoding='utf-8'`, vérifiez que le fichier SQL n'est pas corrompu

### Table nomenclature_pcs_ese existe déjà
**Problème** : UNIQUE constraint failed
**Solution** : Le script fait un `DROP TABLE IF EXISTS` automatiquement

### Libellés emploi non affichés
**Problème** : Colonne vide dans le tableau
**Solution** :
```bash
# Vérifier que la nomenclature est importée
python import_nomenclature.py

# Relancer l'application
python app.py
```

### Graphiques Groupe CSP ne s'affichent pas
**Problème** : Erreur JavaScript dans la console
**Solution** : Vérifiez que `evolution.par_groupe` est bien transmis au template

## 📝 Documentation

### Fichiers de documentation
1. **README.md** - Documentation principale complète
2. **CHANGELOG.md** - Historique des versions et modifications
3. **GIT_GUIDE.md** - Guide pour commit et push Git
4. **REPRISE_PROJET.md** - Ce fichier (guide de reprise)
5. **DEPLOIEMENT.md** - Guide de déploiement en production
6. **NOTES.md** - Notes diverses du projet

### Documentation externe
- [DSN 2025.1](https://dsn-info.custhelp.com/) - Documentation officielle DSN
- [Nomenclature PCS-ESE](https://www.insee.fr/fr/information/2406153) - INSEE
- [Index Égalité](https://travail-emploi.gouv.fr/droit-du-travail/egalite-professionnelle-discrimination-et-harcelement/indexegapro) - Ministère du Travail

## 🔄 Prochaines étapes pour Git

### Étape 1 : Commit des modifications
```bash
cd D:\ClaudeProjects\opendsn2
git add .
git commit -m "feat: v2.0.0 - Nomenclature PCS-ESE complète et distinction Groupe/CSP"
```

### Étape 2 : Push vers GitHub
```bash
git push origin master
```

### Étape 3 : Créer une release
1. Aller sur GitHub → Releases
2. "Draft a new release"
3. Tag : `v2.0.0`
4. Titre : `v2.0.0 - Nomenclature PCS-ESE complète`
5. Description : Copier depuis CHANGELOG.md

Voir **GIT_GUIDE.md** pour tous les détails.

## 🎓 Compétences requises pour maintenir le projet

### Backend
- **Python 3.11+** : Connaissance de base
- **Flask 3.0** : Routes, templates, sessions
- **SQLite** : Requêtes SQL basiques
- **Pandas** : Manipulation de DataFrames

### Frontend
- **HTML5/CSS3** : Structure et style
- **Bootstrap 5** : Composants et grille
- **JavaScript ES6** : Manipulation DOM, événements
- **Chart.js 4.4** : Création de graphiques

### DSN
- **Format DSN** : Structures S10, S20, S21
- **Rubriques** : Identification, contrat, rémunération
- **Nomenclature PCS-ESE** : Groupes, CSP, codes emploi

## 📞 Contact et support

**Auteur** : Sébastien Blochet
**GitHub** : [@neobloblo](https://github.com/neobloblo)
**Projet** : [OpenDSN](https://github.com/neobloblo/opendsn)

**Pour ouvrir une issue** :
1. Aller sur https://github.com/neobloblo/opendsn/issues
2. Cliquer sur "New issue"
3. Décrire le problème avec :
   - Version de l'application
   - Étapes pour reproduire
   - Comportement attendu vs observé
   - Logs si disponibles

## ✅ Checklist de reprise

- [ ] Environnement virtuel activé
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Nomenclature importée (412 codes)
- [ ] Application lancée et accessible
- [ ] Nouvelle page CSP testée
- [ ] Graphiques Groupe CSP vérifiés
- [ ] Tableau récapitulatif salarié testé
- [ ] Documentation lue (README.md, CHANGELOG.md)
- [ ] Prêt pour commit Git

## 🎉 Bon travail !

Le projet est maintenant bien documenté et prêt pour la reprise ou le déploiement.

---

**Dernière mise à jour** : 2025-11-07
**Version** : 2.0.0
**Statut** : ✅ Production Ready
