# 🚀 Guide de Déploiement - Application DSN

## Résumé : Pourquoi PAS Vercel ?

❌ **Vercel n'est PAS adapté** pour cette application car :
- Architecture **serverless** → pas de système de fichiers persistant
- Les fichiers uploadés (`uploads/`) seraient **perdus** après chaque requête
- La base SQLite (`dsn.db`) ne persisterait pas
- Timeout de 10-60 secondes (trop court pour analyses DSN)

## ✅ Solutions Recommandées

---

## Option 1 : Railway (⭐ RECOMMANDÉ - Le plus simple)

**⚠️ Note importante :** L'application utilise SQLite qui nécessite des dépendances système. Le déploiement utilise Docker pour garantir un environnement stable.

**Avantages :**
- ✅ Déploiement en 5 minutes
- ✅ Flask natif supporté
- ✅ Système de fichiers persistant
- ✅ Base SQLite fonctionne
- ✅ HTTPS automatique
- ✅ Logs en temps réel
- ✅ Redéploiement automatique depuis GitHub

**Prix :** Gratuit (500h/mois) ou $5/mois

### Étapes de déploiement Railway :

1. **Créer un compte** sur [railway.app](https://railway.app)

2. **Créer un nouveau projet** :
   - Cliquer sur "New Project"
   - Sélectionner "Deploy from GitHub"
   - Autoriser Railway à accéder à votre repo GitHub
   - Sélectionner le repo `neobloblo/opendsn`

3. **Configuration automatique** :
   Railway détecte automatiquement le `Dockerfile` et build l'image Docker avec :
   - Python 3.11-slim
   - SQLite3 et dépendances système
   - Dépendances Python depuis `requirements.txt`
   - Gunicorn pour la production

4. **Générer un domaine public** :
   - Aller dans l'onglet **Settings** du service
   - Chercher la section **"Networking"** ou **"Public Networking"**
   - Cliquer sur **"Generate Domain"**
   - Railway crée automatiquement : `https://opendsn-production-xxxx.up.railway.app`

5. **Vérifier le déploiement** :
   - Aller dans l'onglet **"Deployments"**
   - Cliquer sur le dernier déploiement
   - Consulter les **"Deploy Logs"** pour vérifier que :
     - Docker build réussit
     - SQLite est installé
     - Gunicorn démarre correctement

6. **Variables d'environnement (optionnel)** :
   - Dans l'interface Railway → "Variables"
   - Ajouter `FLASK_ENV=production` (déjà en production par défaut)

**C'est tout ! 🎉** L'app est en ligne.

---

## Option 2 : Render

**Avantages :**
- ✅ Similaire à Railway
- ✅ Interface très claire
- ✅ Tier gratuit généreux
- ✅ Base de données PostgreSQL incluse (si besoin)

**Prix :** Gratuit (750h/mois) ou $7/mois

### Étapes de déploiement Render :

1. **Créer un compte** sur [render.com](https://render.com)

2. **Créer un Web Service** :
   - Cliquer "New +" → "Web Service"
   - Connecter votre repo GitHub
   - Sélectionner le repo `dsn`

3. **Configuration** :
   - **Name** : `dsn-analyzer`
   - **Environment** : `Python 3`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn app:app`

4. **Déployer** :
   - Cliquer "Create Web Service"
   - Render build et déploie automatiquement
   - Domaine HTTPS : `https://dsn-analyzer.onrender.com`

---

## Option 3 : DigitalOcean App Platform

**Avantages :**
- ✅ Très stable et fiable
- ✅ Documentation excellente
- ✅ Bon rapport qualité/prix

**Prix :** $5/mois

### Étapes :

1. Créer un compte DigitalOcean
2. "Apps" → "Create App"
3. Connecter GitHub → sélectionner repo
4. DigitalOcean détecte automatiquement Flask
5. Déployer

---

## Option 4 : Docker + VPS (OVH, Hetzner, etc.)

Pour un **contrôle total** et un **coût minimal** (3-5€/mois).

### Fichiers fournis :

Le projet contient déjà :
- `Procfile` → commande de démarrage
- `requirements.txt` → avec gunicorn
- `runtime.txt` → Python 3.11
- `.gitignore` → fichiers à exclure

### Commandes pour tester en local avec gunicorn :

```bash
# Installer gunicorn
pip install gunicorn

# Tester en local
gunicorn app:app --bind 0.0.0.0:8050

# Accéder à http://localhost:8050
```

---

## 🔒 Checklist Sécurité Production

Avant de déployer, vérifiez :

- [ ] Mode debug désactivé (`FLASK_ENV=production`)
- [ ] `.gitignore` créé (ne pas commit venv, uploads, .env)
- [ ] Fichiers uploads limités aux formats DSN (`.edi`, `.xml`)
- [ ] Taille max d'upload configurée (50 MB)
- [ ] HTTPS activé (automatique sur Railway/Render)
- [ ] Variables sensibles dans variables d'environnement (pas en dur dans le code)

---

## 📊 Monitoring (optionnel)

### Sentry (erreurs en temps réel)

```bash
pip install sentry-sdk[flask]
```

Ajouter dans `app.py` :
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="VOTRE_DSN_SENTRY",
    integrations=[FlaskIntegration()],
)
```

---

## 🎯 Ma Recommandation Finale

**Pour démarrer rapidement** :
→ **Railway** (configuration zero, déploiement en 5 min)

**Pour du long terme avec base PostgreSQL** :
→ **Render** (tier gratuit excellent + base incluse)

**Pour du full contrôle** :
→ **Docker sur VPS OVH** (3€/mois)

---

## 📝 Commandes utiles

```bash
# Tester en local avec gunicorn
gunicorn app:app --bind 0.0.0.0:8050

# Vérifier les dépendances
pip list

# Freezer les dépendances exactes
pip freeze > requirements.txt

# Test de l'app
python app.py
```

---

## 🆘 Support

En cas de problème :
1. Consulter les logs de la plateforme de déploiement
2. Vérifier que toutes les dépendances sont dans `requirements.txt`
3. Tester en local avec gunicorn avant de déployer
4. Vérifier que le port est bien configuré (`PORT` env variable)

---

**Créé le** : 05/11/2025
**Dernière mise à jour** : 05/11/2025
