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

### 🎨 Interface moderne
- Design moderne avec gradients et animations CSS
- Graphiques interactifs Chart.js
- Tooltips contextuels pour guider l'utilisateur
- Responsive Bootstrap 5
- Sans éléments collapse (interface toujours visible)

### 📂 Gestion des fichiers DSN
- Upload multi-fichiers (jusqu'à 12 mois)
- Support des formats : `.edi`, `.xml`, `.txt`, `.dsn`
- Analyse mono-fichier ou multi-mois
- Filtrage par types de rémunération
- Date de référence personnalisable

### 🔍 Parser DSN complet
- Structure S10 (Entreprise)
- Structure S20 (Établissement)
- Structure S21 (Salarié)
  - S21.G00.40 : Identité (nom, prénom, sexe, date naissance)
  - S21.G00.50 : Contrat (CSP, position convention)
  - S21.G00.51 : Rémunération (par période et type)

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
├── app.py                      # Application Flask principale
├── dsn_parser.py               # Parser DSN et calcul indicateurs
├── requirements.txt            # Dépendances Python
├── Procfile                    # Configuration déploiement
├── runtime.txt                 # Version Python
├── dsn.db                      # Base SQLite (structures DSN)
├── templates/
│   ├── base.html              # Template de base
│   ├── egalite_hf.html        # Page Index Égalité H/F
│   ├── accueil.html           # Page d'accueil
│   ├── structures.html        # Liste structures DSN
│   └── rubriques.html         # Liste rubriques DSN
├── uploads/                   # Fichiers DSN uploadés
└── cahier_technique/          # Documentation DSN 2025.1
```

### Utilisation

#### 1. Upload de fichiers DSN
- Sélectionner 1 à 12 fichiers DSN mensuels
- Formats acceptés : `.edi`, `.xml`, `.txt`, `.dsn`

#### 2. Configuration de l'analyse
- Choisir les types de rémunération à inclure (par défaut : 003 - Salaire rétabli)
- Définir la date de référence pour le calcul des âges

#### 3. Résultats
- Scores des 5 indicateurs
- Graphiques de répartition H/F
- Graphiques des scores par indicateur
- Détail par groupe CSP × Âge
- Liste des salariés avec leurs rémunérations

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
