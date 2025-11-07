# 📊 OpenDSN

**Analyseur DSN avec calcul automatique de l'Index Égalité Professionnelle**

Application web Flask pour analyser les fichiers DSN (Déclaration Sociale Nominative) et calculer automatiquement l'Index Égalité Professionnelle Femmes-Hommes selon la réglementation française.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Fonctionnalités

### 📈 Calcul de l'Index Égalité Professionnelle
- **Indicateur 1** (40 pts) : Écart de rémunération entre femmes et hommes (par CSP et tranche d'âge)
- **Indicateur 2** (20 pts) : Écart d'augmentations individuelles
- **Indicateur 3** (15 pts) : Écart de promotions
- **Indicateur 4** (15 pts) : Pourcentage de salariées augmentées après un congé maternité
- **Indicateur 5** (10 pts) : Nombre de personnes du sexe sous-représenté dans les 10 plus hautes rémunérations

### 📊 Évolution de l'effectif
- **Suivi multi-périodes** : Analyse jusqu'à 24 fichiers DSN mensuels
- **Détection automatique des entrées/sorties** : Basée sur les dates réelles d'embauche (S21.G00.40.001) et de sortie (S21.G00.62.001)
- **Statistiques globales** : Effectif initial, final, variation, effectif moyen, âge moyen
- **Graphiques interactifs** :
  - Évolution de l'effectif total dans le temps (valeurs entières uniquement)
  - Répartition Hommes/Femmes (valeurs entières uniquement)
  - Entrées et sorties mensuelles
  - Pyramide des âges (tranches de 5 ans, valeurs entières)
  - Évolution des moyennes d'âge par sexe (Hommes vs Femmes)
  - **Répartition par Groupe CSP** : Graphique en camembert et courbes d'évolution
- **Détails au survol** : Nom, prénom, date d'embauche/sortie pour chaque mouvement
- **Tableau détaillé** : Vue mensuelle avec :
  - Effectif total et âge moyen global
  - Effectif Hommes et âge moyen Hommes
  - Effectif Femmes et âge moyen Femmes
  - Entrées/sorties avec tooltips
- **Récapitulatif par salarié** : Tableau détaillé avec sélecteur de période affichant :
  - Matricule, NIR, Nom, Prénom, Sexe
  - Date de naissance et Âge
  - **Groupe CSP** (ex: "Ouvriers", "Cadres")
  - **CSP** avec code et libellé (ex: "63 - Ouvriers qualifiés...")
  - **Code emploi PCS-ESE** (ex: "636d")
  - **Libellé emploi** automatiquement récupéré depuis la nomenclature
  - Dates d'embauche et de sortie
  - Statut (Actif, Entrée, Sortie, Entrée & Sortie)

### 📋 Catégories Socioprofessionnelles (PCS-ESE)
- **Page dédiée** à la nomenclature PCS-ESE
- **5 Groupes** de CSP (1er chiffre du code PCS-ESE) :
  - 2 : Artisans, commerçants et chefs d'entreprise
  - 3 : Cadres et professions intellectuelles supérieures
  - 4 : Professions intermédiaires
  - 5 : Employés
  - 6 : Ouvriers
- **CSP détaillées** (2 premiers chiffres du code PCS-ESE)
- **Nomenclature complète** : 412 codes PCS-ESE avec libellés
- **Intégration automatique** : Libellés d'emploi récupérés automatiquement depuis la base de données
- **Documentation** : Utilisation dans l'application et source INSEE

### 🎨 Interface moderne
- Design moderne avec gradients et animations CSS
- Graphiques interactifs Chart.js
- Tooltips contextuels pour guider l'utilisateur
- Responsive Bootstrap 5
- Sans éléments collapse (interface toujours visible)

### 📂 Gestion des fichiers DSN
- Upload multi-fichiers (jusqu'à 24 mois pour l'évolution de l'effectif, 12 mois pour l'Index Égalité)
- Support des formats : `.edi`, `.xml`, `.txt`, `.dsn`
- Analyse mono-fichier ou multi-mois
- Tri automatique par date de déclaration (S20.G00.05.005)
- Filtrage par types de rémunération
- Date de référence personnalisable

### 🔍 Parser DSN complet
- Structure S10 (Entreprise)
- Structure S20 (Établissement)
  - S20.G00.05.005 : Date du mois principal déclaré
- Structure S21 (Salarié)
  - S21.G00.30 : Identification
    - S21.G00.30.001 : NIR (avec détection du sexe)
    - S21.G00.30.002 : Nom de famille
    - S21.G00.30.004 : Prénom
    - S21.G00.30.006 : Date de naissance
    - S21.G00.30.019 : Matricule (identifiant unique)
  - S21.G00.40 : Contrat
    - S21.G00.40.001 : Date d'embauche
    - S21.G00.40.002 : Statut conventionnel (fallback pour Groupe CSP)
    - **S21.G00.40.004 : Code PCS-ESE** (prioritaire pour Groupe et CSP)
      - **Groupe** : 1er chiffre (2-6)
      - **CSP** : 2 premiers chiffres
      - **Libellé emploi** : Récupéré depuis la nomenclature (412 codes)
  - S21.G00.51 : Rémunération (par période et type)
  - S21.G00.62 : Fin de contrat
    - S21.G00.62.001 : Date de fin de contrat (sortie)

## 🚀 Démarrage rapide

### Prérequis
- Python 3.11+
- pip

### Installation locale

```bash
# Cloner le repo
git clone https://github.com/neobloblo/opendsn.git
cd opendsn

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Importer la nomenclature PCS-ESE (si nécessaire)
python import_nomenclature.py

# Lancer l'application
python app.py
```

L'application sera accessible sur **http://localhost:8050**

## 🌐 Déploiement en production

L'application est prête pour le déploiement sur :

### Railway (Recommandé)
1. Aller sur [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub"
3. Sélectionner `neobloblo/opendsn`
4. Railway déploie automatiquement !

### Render
1. Aller sur [render.com](https://render.com)
2. "New +" → "Web Service"
3. Connecter GitHub → Sélectionner `opendsn`
4. Render configure automatiquement

### Autres plateformes
L'application inclut :
- `Procfile` pour Heroku/Railway
- `runtime.txt` pour spécifier Python 3.11
- `requirements.txt` avec Gunicorn
- Configuration production dans `app.py`

Voir [DEPLOIEMENT.md](DEPLOIEMENT.md) pour plus de détails.

## 📖 Documentation

### Structure du projet

```
opendsn/
├── app.py                                  # Application Flask principale
├── dsn_parser.py                           # Parser DSN et calcul indicateurs
├── import_nomenclature.py                  # Script d'import nomenclature PCS-ESE
├── requirements.txt                        # Dépendances Python
├── Procfile                                # Configuration déploiement
├── runtime.txt                             # Version Python
├── dsn.db                                  # Base SQLite (structures DSN + nomenclature)
├── nomenclature_pcs_ese.sql                # Nomenclature PCS-ESE (412 codes)
├── templates/
│   ├── base.html                          # Template de base
│   ├── accueil.html                       # Page d'accueil
│   ├── egalite_hf.html                    # Page Index Égalité H/F
│   ├── evolution_effectif.html            # Page Evolution de l'effectif
│   ├── categories_socioprofessionnelles.html  # Page nomenclature CSP
│   ├── structures.html                    # Liste structures DSN
│   └── rubriques.html                     # Liste rubriques DSN
├── uploads/                               # Fichiers DSN uploadés
└── cahier_technique/                      # Documentation DSN 2025.1
```

### Utilisation

#### 1. Index Égalité Professionnelle
1. Accéder à la page "Égalité Homme-Femme"
2. Sélectionner 1 à 12 fichiers DSN mensuels
3. Choisir les types de rémunération à inclure (par défaut : 003 - Salaire rétabli)
4. Définir la date de référence pour le calcul des âges
5. Consulter les résultats :
   - Scores des 5 indicateurs
   - Graphiques de répartition H/F
   - Détail par groupe CSP × Âge

#### 2. Évolution de l'effectif
1. Accéder à la page "Evolution de l'effectif"
2. Sélectionner 1 à 24 fichiers DSN mensuels
3. Consulter les résultats :
   - Statistiques globales (effectif initial, final, variation, âge moyen)
   - Graphique d'évolution de l'effectif total (valeurs entières)
   - Graphique de répartition Hommes/Femmes (valeurs entières)
   - Graphique des entrées et sorties mensuelles
   - Pyramide des âges au dernier mois (valeurs entières)
   - Graphique d'évolution des moyennes d'âge (Hommes vs Femmes)
   - **Graphiques par Groupe CSP** : Camembert + courbes d'évolution
   - Tableau détaillé avec :
     * Âges moyens par mois (global, hommes, femmes)
     * Tooltips pour les entrées/sorties avec noms et dates
   - **Récapitulatif détaillé par salarié** :
     * Sélecteur de période (par défaut: dernière période)
     * 14 colonnes d'informations incluant Groupe, CSP et libellé emploi

#### 3. Catégories Socioprofessionnelles
1. Accéder à la page "Catégories Socioprofessionnelles"
2. Consulter :
   - Les 5 groupes de CSP avec codes internes
   - Les CSP détaillées (2 chiffres)
   - La nomenclature complète (412 codes PCS-ESE) organisée par groupe
   - Documentation sur l'utilisation dans l'application

## 🔧 Technologies utilisées

- **Backend** : Flask 3.0, Python 3.11
- **Frontend** : Bootstrap 5, Chart.js 4.4
- **Base de données** : SQLite
- **Parser** : Pandas, chardet
- **Production** : Gunicorn

## 📊 Calcul des indicateurs

### Indicateur 1 : Écart de rémunération (40 points)
Calcule l'écart de rémunération moyenne entre femmes et hommes par groupe CSP × Tranche d'âge.
Barème officiel : écart ≤ 1% = 40 pts, ≤ 2% = 39 pts, etc.

### Indicateur 2 : Augmentations (20 points)
Compare les taux d'augmentation individuelle entre femmes et hommes.
Seuil de détection : +5% minimum entre premier et dernier mois.

### Indicateur 3 : Promotions (15 points)
Compare les taux de promotion entre femmes et hommes.
Détection : changement de CSP vers un niveau supérieur.

### Indicateur 4 : Congé maternité (15 points)
Vérifie que les salariées ont été augmentées à leur retour de congé maternité.
**Note** : Nécessite la rubrique S21.G00.60 (non calculable actuellement).

### Indicateur 5 : Top 10 (10 points)
Compte le nombre de personnes du sexe sous-représenté dans les 10 plus hautes rémunérations.
10 points si au moins 4 personnes, sinon 0.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Reporter des bugs via les [Issues](https://github.com/neobloblo/opendsn/issues)
- Proposer des améliorations
- Soumettre des Pull Requests

## 📄 License

MIT License - Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 📞 Contact

**Auteur** : Sébastien Blochet
**GitHub** : [@neobloblo](https://github.com/neobloblo)
**Projet** : [OpenDSN](https://github.com/neobloblo/opendsn)

## 🙏 Remerciements

- Documentation officielle DSN 2025.1
- [Flask](https://flask.palletsprojects.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Chart.js](https://www.chartjs.org/)

---

**⚠️ Note légale** : Cet outil est fourni à titre informatif. Vérifiez toujours les résultats avec un expert-comptable ou un juriste pour les déclarations officielles.

**🇫🇷 Made in France** pour faciliter le calcul de l'Index Égalité Professionnelle
