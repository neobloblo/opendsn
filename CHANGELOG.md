# Changelog

Toutes les modifications notables du projet OpenDSN seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-11-07

### ✨ Ajouté

#### Nomenclature PCS-ESE Complète
- **Nouveau fichier** : `nomenclature_pcs_ese.sql` contenant 412 codes PCS-ESE officiels
- **Nouveau script** : `import_nomenclature.py` pour importer la nomenclature dans la base de données
- **Nouvelle table** : `nomenclature_pcs_ese` dans `dsn.db` avec colonnes :
  - `id` : Identifiant unique
  - `code` : Code PCS-ESE (ex: "382a", "524a", "636d")
  - `libelle` : Libellé complet de la profession
  - `categorie_principale` : Catégorie (1-6) pour regroupement

#### Nouvelle Page : Catégories Socioprofessionnelles
- **Route** : `/categories-socioprofessionnelles`
- **Template** : `templates/categories_socioprofessionnelles.html`
- **Contenu** :
  - Section 1 : Les 5 groupes de CSP (1er chiffre) avec codes internes (21-26)
  - Section 2 : Liste des CSP détaillées (2 chiffres) avec groupes parents
  - Section 3 : Nomenclature complète organisée par groupe (accordion interactif)
  - Section informative : Utilisation dans l'application et sources
- **Navigation** : Nouvel onglet dans le menu latéral entre "Rubriques" et "Indicateurs RH"

#### Récapitulatif Détaillé par Salarié (Évolution de l'effectif)
- **Sélecteur de période** : Dropdown pour choisir le mois à afficher (défaut: dernière période)
- **14 colonnes d'informations** :
  1. Matricule
  2. NIR
  3. Nom
  4. Prénom
  5. Sexe
  6. Date de naissance
  7. Âge
  8. **Groupe CSP** (ex: "Ouvriers", "Cadres")
  9. **CSP** (code 2 chiffres + libellé tronqué avec tooltip)
  10. **Code emploi PCS-ESE** (ex: "636d")
  11. **Libellé emploi** (récupéré depuis la nomenclature)
  12. Date embauche
  13. Date sortie
  14. Statut (badges colorés : Actif, Entrée, Sortie, Entrée & Sortie)
- **Mise à jour dynamique** : Table rafraîchie automatiquement lors du changement de période

#### Graphiques par Groupe CSP (Évolution de l'effectif)
- **Graphique en camembert** : Répartition par groupe CSP à la dernière période
  - Affichage des pourcentages et effectifs
  - Date de référence au format (jj/mm/aaaa)
- **Graphique en courbes** : Évolution temporelle des 6 groupes CSP
  - Courbes colorées par groupe
  - Valeurs entières uniquement

### 🔧 Modifié

#### Terminologie : CSP → Groupe + CSP
**Changement majeur** pour respecter la nomenclature officielle PCS-ESE :

**Avant** :
- "CSP" désignait le 1er chiffre du code PCS-ESE

**Maintenant** :
- **Groupe CSP** = 1er chiffre du code PCS-ESE (2, 3, 4, 5, 6)
  - Exemples : "Ouvriers", "Employés", "Cadres"
  - Codes internes : 21-26
- **CSP (Catégorie Socioprofessionnelle)** = 2 premiers chiffres du code PCS-ESE
  - Exemples : "38", "52", "63"
  - Libellés complets récupérés depuis la nomenclature

#### Parser DSN (`dsn_parser.py`)
**Fonctions renommées** :
- `_determine_csp_from_pcs_ese()` → `_determine_groupe_from_pcs_ese()`
- `_csp_to_code()` → `_groupe_to_code()`
- `_determine_csp_from_statut()` : Documentation mise à jour (retourne maintenant un Groupe)

**Nouvelles fonctions** :
- `_extract_csp_from_pcs_ese(code_pcs_ese)` : Extrait la CSP (2 chiffres)
- `get_libelle_csp(csp_code)` : Récupère le libellé de la CSP depuis la nomenclature
- `_load_nomenclature_pcs_ese()` : Charge la nomenclature avec cache (classe)

**Nouvelles données stockées** par salarié :
- `groupe` : Libellé du groupe (ex: "Ouvriers")
- `groupe_code` : Code du groupe (ex: "21")
- `csp` : Code CSP à 2 chiffres (ex: "63")
- `csp_libelle` : Libellé de la CSP
- `libelle_emploi` : Libellé de la profession (depuis nomenclature)

#### Application Flask (`app.py`)
**Variables renommées** (route `/evolution-effectif`) :
- `par_csp` → `par_groupe`
- `csp_count` → `groupe_count`
- `csp_code` → `groupe_code`
- `csp_libelle` → `groupe_libelle`

**Nouvelles variables** transmises au template :
- `groupe`, `groupe_code` : Informations sur le groupe
- `csp`, `csp_libelle` : Informations sur la CSP

#### Templates HTML
**Fichier** : `templates/evolution_effectif.html`

**Modifications des titres** :
- "Répartition CSP" → "Répartition par Groupe CSP"
- "Évolution par catégorie socioprofessionnelle" → "Évolution par groupe de catégorie socioprofessionnelle"

**IDs des canvas modifiés** :
- `chartCSPPie` → `chartGroupePie`
- `chartCSP` → `chartGroupe`

**Variables JavaScript renommées** :
- `parCSP` → `parGroupe`
- `cspLabels` → `groupeLabels`
- `cspColors` → `groupeColors`
- `cspDatasets` → `groupeDatasets`

**Nouvelles colonnes dans le tableau des salariés** :
- Colonne "Groupe" : Affiche le groupe CSP (ex: "Ouvriers")
- Colonne "CSP" : Affiche code + libellé tronqué avec tooltip complet

**Fichier** : `templates/base.html`
- Ajout du lien "Catégories Socioprofessionnelles" dans la navigation

### 📚 Documentation

#### README.md
- Ajout section "Catégories Socioprofessionnelles (PCS-ESE)"
- Mise à jour section "Évolution de l'effectif" avec nouvelles fonctionnalités
- Mise à jour section "Parser DSN complet" avec distinction Groupe/CSP
- Mise à jour "Structure du projet" avec nouveaux fichiers
- Ajout étape d'import de la nomenclature dans l'installation
- Mise à jour "Utilisation" avec nouvelle page CSP

#### CHANGELOG.md
- Création de ce fichier pour suivre les modifications

### 🐛 Corrections

- **Précision terminologique** : Distinction claire entre Groupe (1 chiffre) et CSP (2 chiffres)
- **Cohérence des données** : Toutes les références à "CSP" ont été vérifiées et corrigées
- **Libellés emploi** : Ajout des libellés manquants récupérés automatiquement

### 🔄 Changements techniques

#### Base de données (`dsn.db`)
**Nouvelle table** : `nomenclature_pcs_ese`
```sql
CREATE TABLE nomenclature_pcs_ese (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    libelle TEXT NOT NULL,
    categorie_principale INTEGER
);
```

#### Performance
- **Cache de nomenclature** : La nomenclature PCS-ESE est chargée une seule fois au niveau de la classe DSNParser
- **Réutilisation** : Évite les requêtes SQL répétées lors du parsing de multiples fichiers

### 📦 Fichiers ajoutés

1. `nomenclature_pcs_ese.sql` (412 lignes)
2. `import_nomenclature.py` (51 lignes)
3. `templates/categories_socioprofessionnelles.html` (235 lignes)
4. `CHANGELOG.md` (ce fichier)

### 📝 Fichiers modifiés

1. `dsn_parser.py` : +80 lignes (nouvelles fonctions nomenclature)
2. `app.py` : +57 lignes (nouvelle route + modifications variables)
3. `templates/evolution_effectif.html` : Modifications majeures (titres, variables JS, colonnes)
4. `templates/base.html` : +3 lignes (nouveau lien navigation)
5. `README.md` : Mise à jour complète

---

## [1.0.0] - 2025-10-XX

### Ajouté
- Version initiale de l'application OpenDSN
- Calcul de l'Index Égalité Professionnelle (5 indicateurs)
- Analyse de l'évolution de l'effectif
- Parser DSN complet (structures S10, S20, S21)
- Interface web Flask avec Bootstrap 5
- Graphiques interactifs Chart.js
- Base de données SQLite avec structures et rubriques DSN
- Support multi-fichiers (jusqu'à 24 mois)
- Détection automatique des entrées/sorties
- Pyramide des âges
- Configuration pour déploiement (Railway, Render, Heroku)

---

## Format du Changelog

### Types de modifications
- **Ajouté** : Nouvelles fonctionnalités
- **Modifié** : Changements dans les fonctionnalités existantes
- **Déprécié** : Fonctionnalités qui seront supprimées
- **Supprimé** : Fonctionnalités supprimées
- **Corrigé** : Corrections de bugs
- **Sécurité** : Correctifs de vulnérabilités

### Émojis utilisés
- ✨ Ajouté
- 🔧 Modifié
- 📚 Documentation
- 🐛 Corrections
- 🔒 Sécurité
- 🗑️ Supprimé
- ⚠️ Déprécié
- 🔄 Changements techniques
