# Notes de développement - OpenDSN

## Session du 06/11/2025 - Utilisation du code PCS-ESE

### Amélioration : Détermination de la CSP via S21.G00.40.004

#### Modifications apportées

1. **Nouvelle rubrique DSN extraite** (dsn_parser.py)
   - S21.G00.40.004 : Code profession et catégorie socioprofessionnelle (PCS-ESE)
   - Cette rubrique est maintenant utilisée en priorité pour déterminer la CSP
   - Fallback sur S21.G00.40.002 (Statut conventionnel) si PCS-ESE non disponible

2. **Mapping PCS-ESE vers CSP** (dsn_parser.py:348-381)
   - Nouvelle fonction `_determine_csp_from_pcs_ese()`
   - Le code PCS-ESE est composé de 3 chiffres + 1 lettre (ex: "352a", "546d", "621a")
   - Le premier chiffre indique la grande catégorie selon la nomenclature INSEE:
     * 2: Artisans, commerçants et chefs d'entreprise
     * 3: Cadres et professions intellectuelles supérieures → "Ingénieurs et cadres"
     * 4: Professions intermédiaires → "Techniciens et agents de maîtrise"
     * 5: Employés
     * 6: Ouvriers

3. **Conversion CSP vers code numérique** (dsn_parser.py:383-415)
   - Nouvelle fonction `_csp_to_code()`
   - Mapping pour l'Index Égalité et l'évolution de l'effectif:
     * 21 : Ouvriers
     * 22 : Employés
     * 23 : Techniciens et agents de maîtrise
     * 24 : Ingénieurs et cadres
     * 25 : Artisans, commerçants
     * 26 : Chefs d'entreprise

4. **Utilisation dans app.py** (app.py:439, 459-460)
   - Récupération du `csp_code` numérique depuis les salariés
   - Comptage par code CSP numérique (21-26) pour l'évolution de l'effectif
   - Maintien de la compatibilité avec le code existant

#### Avantages

- **Plus précis** : Le code PCS-ESE (INSEE) est une nomenclature officielle et standardisée
- **Automatique** : La CSP est déduite directement du code PCS-ESE sans intervention manuelle
- **Compatible** : Fallback sur S21.G00.40.002 si PCS-ESE non disponible
- **Groupes socioprofessionnels** : Les codes 21-26 permettent un suivi par CSP dans l'évolution de l'effectif

#### Tests effectués

```python
# Exemples de codes PCS-ESE et leur mapping:
352a -> Ingénieurs et cadres (code 24)       # Journaliste
546d -> Employés (code 22)                    # Hôtesse/steward
621a -> Ouvriers (code 21)                    # Ouvrier qualifié
463b -> Techniciens et agents de maîtrise (code 23)  # Représentant
231a -> Artisans, commerçants (code 25)       # Artisan
```

#### Documentation

- README.md : Mise à jour de la section Parser DSN avec la nouvelle rubrique S21.G00.40.004
- NOTES.md : Documentation complète du mapping PCS-ESE

---

## Session du 06/11/2025 - Suite

### Améliorations apportées : Affichage des âges moyens

#### Modifications apportées

1. **Affichage des nombres entiers uniquement** (evolution_effectif.html)
   - Configuration Chart.js avec `stepSize: 1` sur tous les graphiques
   - Callback sur les axes Y pour filtrer et afficher uniquement les valeurs entières
   - Appliqué sur :
     * Graphique d'évolution de l'effectif total
     * Graphique de répartition Hommes/Femmes
     * Pyramide des âges (axe X)
     * Graphique d'évolution des moyennes d'âge

2. **Nouveau graphique : Évolution des moyennes d'âge** (app.py + evolution_effectif.html)
   - Calcul mensuel de l'âge moyen global, hommes et femmes (app.py:497-515)
   - Ajout des champs dans evolution_data :
     * `age_moyen` : Âge moyen global (tous sexes confondus)
     * `age_moyen_hommes` : Âge moyen des hommes
     * `age_moyen_femmes` : Âge moyen des femmes
   - Graphique Chart.js avec deux courbes :
     * Ligne bleue pour l'âge moyen des hommes
     * Ligne rose pour l'âge moyen des femmes
   - Layout côte-à-côte avec la pyramide des âges (col-md-6)

3. **Enrichissement du tableau détaillé** (evolution_effectif.html:246-269)
   - Ajout de 3 nouvelles colonnes après les effectifs :
     * "Âge moyen" (après Effectif total)
     * "Âge moyen H" (après Hommes)
     * "Âge moyen F" (après Femmes)
   - Affichage en gris (text-muted) avec suffixe " ans"

#### Détails techniques

**Calcul des âges moyens (app.py:497-515) :**
```python
# Calculer les moyennes d'âge
age_moyen_h = int(round(sum(ages_hommes) / len(ages_hommes))) if ages_hommes else 0
age_moyen_f = int(round(sum(ages_femmes) / len(ages_femmes))) if ages_femmes else 0
# Âge moyen global (tous sexes confondus)
ages_tous = ages_hommes + ages_femmes
age_moyen_global = int(round(sum(ages_tous) / len(ages_tous))) if ages_tous else 0
```

**Configuration Chart.js pour nombres entiers (evolution_effectif.html:590-597) :**
```javascript
ticks: {
    stepSize: 1,
    callback: function(value) {
        if (Number.isInteger(value)) {
            return value;
        }
    }
}
```

#### Affichage

**Graphiques :**
- Tous les graphiques affichent maintenant uniquement des valeurs entières sur leurs axes
- Le graphique d'évolution des âges moyens permet de suivre l'évolution temporelle de l'âge moyen par sexe

**Tableau détaillé :**
| Période | Effectif total | Âge moyen | Hommes | Âge moyen H | Femmes | Âge moyen F | Entrées | Sorties | Variation |
|---------|----------------|-----------|---------|-------------|---------|-------------|---------|---------|-----------|
| MM/AAAA | 150            | 42 ans    | 85      | 43 ans      | 65      | 40 ans      | +5      | -2      | +3        |

#### Git

**Commit d53f5e4** : Ajout des moyennes d'âge et affichage entier sur tous les graphiques
- Graphiques avec valeurs entières uniquement (stepSize: 1 + callback filter)
- Nouveau graphique : Évolution des moyennes d'âge (Hommes vs Femmes)
- Tableau détaillé enrichi avec 3 colonnes d'âge moyen (global, H, F)
- Calcul mensuel des âges moyens dans app.py
- Documentation mise à jour (README.md + NOTES.md)

---

## Session du 06/11/2025 - Début

### Fonctionnalité développée : Évolution de l'effectif

#### Modifications apportées

1. **Extraction de nouvelles rubriques DSN** (dsn_parser.py)
   - S21.G00.30.002 : Nom de famille (déjà présent)
   - S21.G00.30.004 : Prénom (déjà présent)
   - S21.G00.40.001 : Date d'embauche
   - S21.G00.62.001 : Date de sortie (NOUVEAU)

2. **Nouvelle logique de détection des entrées/sorties** (app.py)
   - Fonction `date_dans_mois()` pour comparer une date DDMMYYYY avec le mois de déclaration
   - Détection des entrées : `date_embauche` correspond au mois en cours
   - Détection des sorties : `date_sortie` correspond au mois en cours
   - Abandon de la logique de comparaison entre mois consécutifs

3. **Interface utilisateur** (evolution_effectif.html)
   - Affichage des détails au survol dans le graphique Chart.js :
     * Entrées : nom, prénom, date d'embauche
     * Sorties : nom, prénom, date de sortie
   - Tooltips Bootstrap dans le tableau détaillé
   - Pyramide des âges avec ordre inversé (âges élevés en haut)

4. **Calculs statistiques**
   - Effectif moyen : nombres entiers uniquement
   - Âge moyen : calcul et affichage dans les statistiques globales
   - Pyramide des âges calculée au dernier jour du mois le plus récent

5. **Git et documentation**
   - Initialisation du dépôt git
   - Commit initial avec toutes les modifications
   - Mise à jour du README.md avec la nouvelle fonctionnalité

#### Rubriques DSN utilisées

**Identification des salariés :**
- S21.G00.30.001 : NIR (premier caractère = sexe : 1=homme, 2=femme)
- S21.G00.30.002 : Nom de famille
- S21.G00.30.004 : Prénom
- S21.G00.30.006 : Date de naissance (DDMMYYYY)
- S21.G00.30.019 : Matricule (identifiant unique)

**Données de contrat :**
- S20.G00.05.005 : Date du mois principal déclaré (01MMYYYY)
- S21.G00.40.001 : Date d'embauche (DDMMYYYY)
- S21.G00.40.002 : Statut conventionnel (pour CSP)
- S21.G00.62.001 : Date de fin de contrat/sortie (DDMMYYYY)

#### Points techniques importants

1. **Format des dates :**
   - Date de déclaration : "01MMYYYY" (toujours le 1er du mois)
   - Autres dates : "DDMMYYYY" (jour, mois, année)

2. **Identifiant unique :**
   - Priorité au matricule (S21.G00.30.019)
   - Fallback sur NIR (S21.G00.30.001) si pas de matricule

3. **Tranches d'âge :**
   - <20, 20-24, 25-29, 30-34, 35-39, 40-44, 45-49, 50-54, 55-59, 60-64, 65+
   - Ordre inversé dans la pyramide (65+ en haut, <20 en bas)

4. **Nombres entiers :**
   - Tous les graphiques utilisent des nombres entiers (pas de demi-personne)
   - Effectif moyen arrondi : `int(round(...))`

#### Configuration de l'application

**URL :** http://localhost:8050/evolution-effectif

**Limites :**
- Maximum 24 fichiers DSN mensuels (2 ans de suivi)
- Formats acceptés : .edi, .xml, .txt, .dsn

#### Prochaines améliorations possibles

1. Ajouter des filtres par CSP pour l'évolution de l'effectif
2. Exporter les données en CSV/Excel
3. Ajouter des graphiques d'évolution par CSP
4. Comparer plusieurs périodes (année N vs année N-1)
5. Ajouter un graphique de turnover (taux de rotation)

#### Commandes utiles

```bash
# Lancer l'application
cd opendsn2
python app.py

# Voir l'historique git
git log --oneline

# Voir les modifications non commitées
git status
git diff
```

#### Structure des commits

- Commit f53455a : Ajout de l'évolution de l'effectif avec détection des entrées/sorties
- Commit 5b60f79 : Mise à jour de la documentation - Évolution de l'effectif
- Commit 8397fb4 : Ajout des notes de développement
- Commit d53f5e4 : Ajout des moyennes d'âge et affichage entier sur tous les graphiques
- Commit fed452c : Mise à jour de NOTES.md avec le dernier commit
- Commit b8f40b4 : Utilisation du code PCS-ESE (S21.G00.40.004) pour déterminer la CSP

---

**Dernière mise à jour :** 06/11/2025
**Développeur :** Claude Code + Utilisateur
