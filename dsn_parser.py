"""
Parser pour fichiers DSN (Déclaration Sociale Nominative)
Format: Lignes de 200 caractères avec structure S21.G00.05 (code rubrique)
"""

import chardet
import re
from typing import List, Dict, Any
from collections import defaultdict
from datetime import datetime


class DSNParser:
    """Parser pour fichiers DSN format Phase 3"""

    # Table de correspondance des types de rémunération (S21.G00.51.011)
    TYPES_REMUNERATION = {
        '001': 'Rémunération brute non plafonnée',
        '002': 'Salaire brut (calcul Assurance chômage)',
        '003': 'Salaire rétabli - reconstitué',
        '010': 'Salaire de base',
        '011': 'Avantage en nature - Nourriture',
        '012': 'Heures d\'équivalence',
        '013': 'Heures supplémentaires',
        '014': 'Heures complémentaires',
        '015': 'Complément différentiel de salaire',
        '016': 'Indemnité forfaitaire pour travaux supplémentaires',
        '017': 'Heures de nuit',
        '018': 'Heures de dimanche',
        '019': 'Heures de jours fériés',
        '020': 'Prime d\'ancienneté',
        '021': '[FP] Taux de rémunération situation administrative',
        '022': 'Potentiel nouveau type',
        '023': 'Prime de froid',
        '024': 'Prime d\'habillage / déshabillage',
        '025': 'Prime de salissure',
        '026': 'Prime de panier',
        '027': 'Autre type de rémunération',
    }

    def __init__(self):
        self.blocks = defaultdict(list)
        self.raw_lines = []
        self.current_period = {}  # Pour stocker les dates et type de période en cours
        self.date_reference = None  # Date de référence pour le calcul de l'âge
        self.stats = {
            'total_lines': 0,
            'entreprise': {},
            'salaries': [],
            'contrats': [],
            'versements': []
        }

    def detect_encoding(self, file_path: str) -> str:
        """Détecte l'encodage du fichier DSN"""
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read(10000))
            return result['encoding'] or 'utf-8'

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse un fichier DSN et retourne les données structurées"""
        encoding = self.detect_encoding(file_path)

        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                line = line.rstrip('\n\r')
                if not line:
                    continue

                self.raw_lines.append(line)
                self.stats['total_lines'] += 1

                # Parse la ligne DSN (format: S21.G00.05.001,valeur ou format EDI)
                parsed = self.parse_line(line)
                if parsed:
                    self.blocks[parsed['rubrique']].append(parsed)

                    # Extraction des informations clés
                    self._extract_key_info(parsed)

        return self.get_results()

    def parse_line(self, line: str) -> Dict[str, Any]:
        """Parse une ligne DSN au format standard ou EDI"""
        # Format 1: S21.G00.05.001,valeur (format standard avec virgule)
        # Peut inclure des guillemets simples: S21.G00.05.001,'valeur'
        pattern1 = r'^(S\d{2}\.G\d{2}\.\d{2}\.\d{3}),(.*)$'
        match1 = re.match(pattern1, line)

        if match1:
            rubrique, valeur = match1.groups()
            # Retirer les guillemets simples si présents
            valeur = valeur.strip().strip("'")
            return {
                'rubrique': rubrique,
                'valeur': valeur,
                'raw': line
            }

        # Format 2: EDI - Format positionnel (200 caractères fixes)
        # Les 18 premiers caractères contiennent le code rubrique
        # Le reste contient la valeur
        if len(line) >= 18:
            # Format EDI: S21G00050010001 suivi de la valeur (sans points ni virgule)
            pattern2 = r'^(S\d{2}G\d{2}\d{2}\d{3})(.*)$'
            match2 = re.match(pattern2, line)

            if match2:
                rubrique_edi, valeur = match2.groups()
                # Convertir le format EDI en format standard
                # S21G00050010001 -> S21.G00.05.001
                if len(rubrique_edi) == 15:
                    rubrique_standard = f"{rubrique_edi[0:3]}.{rubrique_edi[3:6]}.{rubrique_edi[6:8]}.{rubrique_edi[8:11]}"
                    return {
                        'rubrique': rubrique_standard,
                        'valeur': valeur.strip(),
                        'raw': line
                    }

        # Format 3: Ligne avec espaces comme séparateurs (certains fichiers EDI)
        pattern3 = r'^(S\d{2}\.G\d{2}\.\d{2}\.\d{3})\s+(.*)$'
        match3 = re.match(pattern3, line)

        if match3:
            rubrique, valeur = match3.groups()
            return {
                'rubrique': rubrique,
                'valeur': valeur.strip(),
                'raw': line
            }

        # Si pas de match, retourne None pour ignorer la ligne
        return None

    def _extract_key_info(self, parsed: Dict[str, Any]):
        """Extrait les informations importantes selon les rubriques"""
        rubrique = parsed['rubrique']
        valeur = parsed['valeur']

        # Informations entreprise (S21.G00.06 = SIRET)
        if rubrique == 'S21.G00.06.001':
            self.stats['entreprise']['siret'] = valeur

        # Raison sociale (S21.G00.11.001)
        elif rubrique == 'S21.G00.11.001':
            self.stats['entreprise']['raison_sociale'] = valeur

        # Informations salarié
        # NIR (S21.G00.30.001)
        elif rubrique == 'S21.G00.30.001':
            # Le premier chiffre du NIR indique aussi le sexe: 1=Homme, 2=Femme
            sexe_from_nir = 'M' if valeur and valeur[0] == '1' else 'F' if valeur and valeur[0] == '2' else None
            self.stats['salaries'].append({'nir': valeur, 'sexe': sexe_from_nir, 'remunerations': []})

        # Nom (S21.G00.30.002)
        elif rubrique == 'S21.G00.30.002':
            if self.stats['salaries']:
                self.stats['salaries'][-1]['nom'] = valeur

        # Prénom (S21.G00.30.004)
        elif rubrique == 'S21.G00.30.004':
            if self.stats['salaries']:
                self.stats['salaries'][-1]['prenom'] = valeur

        # Sexe (S21.G00.30.005) - 1=Homme, 2=Femme
        elif rubrique == 'S21.G00.30.005':
            if self.stats['salaries']:
                self.stats['salaries'][-1]['sexe'] = 'M' if valeur == '1' else 'F' if valeur == '2' else None

        # Matricule (S21.G00.30.019)
        elif rubrique == 'S21.G00.30.019':
            if self.stats['salaries']:
                self.stats['salaries'][-1]['matricule'] = valeur

        # Date de naissance (S21.G00.30.006 ou S21.G00.30.020)
        elif rubrique in ['S21.G00.30.006', 'S21.G00.30.020']:
            if self.stats['salaries']:
                self.stats['salaries'][-1]['date_naissance'] = valeur
                # La tranche d'âge sera calculée après le parsing avec la date de référence

        # Statut du salarié conventionnel (S21.G00.40.002) - Important pour la CSP
        elif rubrique == 'S21.G00.40.002':
            if self.stats['salaries']:
                self.stats['salaries'][-1]['statut_conventionnel'] = valeur
                # Calculer immédiatement la CSP depuis ce code
                self.stats['salaries'][-1]['csp'] = self._determine_csp_from_statut(valeur)

        # Code statut catégoriel Retraite Complémentaire obligatoire (S21.G00.40.003)
        elif rubrique == 'S21.G00.40.003':
            if self.stats['salaries']:
                self.stats['salaries'][-1]['statut_retraite'] = valeur

        # Statut conventionnel (S21.G00.40.007)
        elif rubrique == 'S21.G00.40.007':
            if self.stats['salaries']:
                self.stats['salaries'][-1]['statut'] = valeur

        # Niveau de qualification (S21.G00.40.008)
        elif rubrique == 'S21.G00.40.008':
            if self.stats['salaries']:
                self.stats['salaries'][-1]['qualification'] = valeur

        # Positionnement dans la convention collective (S21.G00.40.041)
        elif rubrique == 'S21.G00.40.041':
            if self.stats['salaries']:
                self.stats['salaries'][-1]['position_convention'] = valeur

        # Date de début de période de rémunération (S21.G00.51.001)
        elif rubrique == 'S21.G00.51.001':
            self.current_period['date_debut'] = valeur

        # Date de fin de période de rémunération (S21.G00.51.002)
        elif rubrique == 'S21.G00.51.002':
            self.current_period['date_fin'] = valeur
            # Utiliser la première date de fin trouvée comme date de référence
            if not self.date_reference:
                self.date_reference = valeur

        # Type de rémunération (S21.G00.51.011)
        elif rubrique == 'S21.G00.51.011':
            self.current_period['type_code'] = valeur
            self.current_period['type_libelle'] = self.TYPES_REMUNERATION.get(valeur, f'Type {valeur}')

        # Montant de rémunération (S21.G00.51.013)
        elif rubrique == 'S21.G00.51.013':
            if self.stats['salaries']:
                try:
                    montant = float(valeur.replace(',', '.'))
                    # Créer un objet rémunération avec le montant, les dates et le type
                    remuneration = {
                        'montant': montant,
                        'date_debut': self.current_period.get('date_debut', ''),
                        'date_fin': self.current_period.get('date_fin', ''),
                        'type_code': self.current_period.get('type_code', ''),
                        'type_libelle': self.current_period.get('type_libelle', '')
                    }
                    self.stats['salaries'][-1]['remunerations'].append(remuneration)
                except ValueError:
                    pass

    def _calculate_age_group(self, date_naissance: str, date_ref: str = None) -> str:
        """
        Calcule la tranche d'âge à partir de la date de naissance

        Args:
            date_naissance: Date au format DDMMYYYY
            date_ref: Date de référence au format DDMMYYYY (par défaut: date du jour)

        Returns:
            Tranche d'âge: '<30', '30-39', '40-49', '50+'
        """
        if not date_naissance or len(date_naissance) != 8:
            return 'Inconnu'

        try:
            # Format DDMMYYYY pour la date de naissance
            jour_naiss = int(date_naissance[0:2])
            mois_naiss = int(date_naissance[2:4])
            annee_naiss = int(date_naissance[4:8])

            date_naiss = datetime(annee_naiss, mois_naiss, jour_naiss)

            # Utiliser la date de référence ou la date du jour
            if date_ref and len(date_ref) == 8:
                jour_ref = int(date_ref[0:2])
                mois_ref = int(date_ref[2:4])
                annee_ref = int(date_ref[4:8])
                date_reference = datetime(annee_ref, mois_ref, jour_ref)
            else:
                date_reference = datetime.now()

            # Calculer l'âge à la date de référence
            age = date_reference.year - date_naiss.year - ((date_reference.month, date_reference.day) < (date_naiss.month, date_naiss.day))

            if age < 30:
                return '<30'
            elif age < 40:
                return '30-39'
            elif age < 50:
                return '40-49'
            else:
                return '50+'
        except:
            return 'Inconnu'

    def _determine_csp_from_statut(self, statut_code: str) -> str:
        """
        Détermine la catégorie socio-professionnelle depuis le code S21.G00.40.002
        (Statut du salarié conventionnel)

        Mapping officiel DSN:
        - 03, 04, 08 = Ingénieurs et cadres
        - 05 = Techniciens et agents de maîtrise
        - 06 = Employés
        - 07 = Ouvriers
        - 01, 02, 09, 10 = Autre

        Args:
            statut_code: Code du statut conventionnel (S21.G00.40.002)

        Returns:
            CSP: 'Ouvriers', 'Employés', 'Techniciens et agents de maîtrise', 'Ingénieurs et cadres'
        """
        if not statut_code:
            return None

        # Retirer les guillemets et espaces
        code = statut_code.strip().strip("'")

        # Mapping selon la norme DSN 2025.1
        mapping = {
            '03': 'Ingénieurs et cadres',  # Cadre dirigeant
            '04': 'Ingénieurs et cadres',  # Autres cadres
            '08': 'Ingénieurs et cadres',  # Agent fonction publique d'Etat
            '05': 'Techniciens et agents de maîtrise',  # Profession intermédiaire
            '06': 'Employés',  # Employé administratif
            '07': 'Ouvriers',  # Ouvriers qualifiés et non qualifiés
        }

        return mapping.get(code, None)

    def _determine_csp(self, position_convention: str, statut: str = None, qualification: str = None) -> str:
        """
        Ancienne fonction conservée pour compatibilité
        Détermine la catégorie socio-professionnelle

        Args:
            position_convention: Position dans la convention collective
            statut: Statut conventionnel
            qualification: Niveau de qualification

        Returns:
            CSP: 'Ouvriers', 'Employés', 'Techniciens et agents de maîtrise', 'Ingénieurs et cadres'
        """
        # Cette fonction devra être affinée selon les conventions collectives
        # Pour l'instant, on utilise une logique simplifiée basée sur les codes

        if not position_convention:
            return None

        pos = position_convention.upper()

        # Logique simplifiée (à adapter selon les conventions réelles)
        if 'CADRE' in pos or 'INGENIEUR' in pos or 'DIRECTEUR' in pos:
            return 'Ingénieurs et cadres'
        elif 'TECH' in pos or 'AGENT' in pos or 'MAITRISE' in pos or 'AM' in pos:
            return 'Techniciens et agents de maîtrise'
        elif 'EMPLOYE' in pos:
            return 'Employés'
        elif 'OUVRIER' in pos:
            return 'Ouvriers'
        else:
            # Si pas de mot-clé, on essaie de deviner par le code numérique
            # Codes bas = ouvriers, codes moyens = employés, etc.
            return None

    def calculer_index_officiel(self, types_filtres: list = None) -> Dict[str, Any]:
        """
        Calcule l'Index Égalité Professionnelle officiel selon la méthodologie gouvernementale

        Args:
            types_filtres: Liste des codes de types de rémunération à inclure

        Returns:
            Dictionnaire avec les détails du calcul et le score
        """
        # Groupes CSP × Tranches d'âge
        groupes = defaultdict(lambda: {'M': [], 'F': []})

        for salarie in self.stats['salaries']:
            sexe = salarie.get('sexe')
            if sexe not in ['M', 'F']:
                continue

            # Récupérer la tranche d'âge (déjà calculée)
            age_group = salarie.get('tranche_age', 'Inconnu')

            # Récupérer la CSP (déjà calculée depuis S21.G00.40.002)
            csp = salarie.get('csp')

            # Ignorer les salariés sans CSP
            if not csp:
                continue

            # Calculer la rémunération totale (filtrée)
            remunerations = salarie.get('remunerations', [])
            if types_filtres:
                remunerations = [
                    r for r in remunerations
                    if isinstance(r, dict) and r.get('type_code') in types_filtres
                ]

            remun_totale = sum(r['montant'] if isinstance(r, dict) else r for r in remunerations) if remunerations else 0

            if remun_totale > 0 and age_group != 'Inconnu':
                cle_groupe = f"{csp}|{age_group}"
                groupes[cle_groupe][sexe].append(remun_totale)

        # Calculer les écarts par groupe
        resultats_groupes = []
        ecarts_non_corriges = []

        for cle_groupe, data in groupes.items():
            csp, age_group = cle_groupe.split('|')

            remun_h = data['M']
            remun_f = data['F']

            # On ne prend en compte que les groupes avec au moins 3 personnes de chaque sexe
            if len(remun_h) < 3 or len(remun_f) < 3:
                continue

            moy_h = sum(remun_h) / len(remun_h)
            moy_f = sum(remun_f) / len(remun_f)

            # Écart en %
            if moy_h > 0:
                ecart_pct = ((moy_h - moy_f) / moy_h) * 100
            else:
                ecart_pct = 0

            resultats_groupes.append({
                'csp': csp,
                'age_group': age_group,
                'nb_hommes': len(remun_h),
                'nb_femmes': len(remun_f),
                'moyenne_h': round(moy_h, 2),
                'moyenne_f': round(moy_f, 2),
                'ecart_pct': round(ecart_pct, 2)
            })

            ecarts_non_corriges.append(abs(ecart_pct))

        # Calcul de l'écart moyen pondéré (selon méthodologie officielle)
        ecart_moyen = sum(ecarts_non_corriges) / len(ecarts_non_corriges) if ecarts_non_corriges else 0

        # Calcul du score (barème indicateur 1: 40 points)
        # Si écart ≤ 0% : 40 points
        # Si écart > 0% et ≤ 1% : 39 points
        # ... jusqu'à écart > 20% : 0 points
        if ecart_moyen <= 0:
            score = 40
        elif ecart_moyen <= 1:
            score = 39
        elif ecart_moyen <= 2:
            score = 38
        elif ecart_moyen <= 3:
            score = 37
        elif ecart_moyen <= 4:
            score = 35
        elif ecart_moyen <= 5:
            score = 33
        elif ecart_moyen <= 6:
            score = 31
        elif ecart_moyen <= 7:
            score = 29
        elif ecart_moyen <= 8:
            score = 27
        elif ecart_moyen <= 9:
            score = 25
        elif ecart_moyen <= 10:
            score = 23
        elif ecart_moyen <= 11:
            score = 21
        elif ecart_moyen <= 12:
            score = 19
        elif ecart_moyen <= 13:
            score = 17
        elif ecart_moyen <= 14:
            score = 14
        elif ecart_moyen <= 15:
            score = 11
        elif ecart_moyen <= 16:
            score = 8
        elif ecart_moyen <= 17:
            score = 5
        elif ecart_moyen <= 18:
            score = 2
        elif ecart_moyen <= 19:
            score = 1
        else:
            score = 0

        return {
            'ecart_moyen_pondere': round(ecart_moyen, 2),
            'score': score,
            'score_max': 40,
            'groupes': sorted(resultats_groupes, key=lambda x: (x['csp'], x['age_group'])),
            'nb_groupes_valides': len(resultats_groupes)
        }

    def calculer_indicateur_augmentations(self, types_filtres: list = None) -> Dict[str, Any]:
        """
        Calcule l'Indicateur 2 - Écart de taux d'augmentations individuelles

        ATTENTION: Nécessite au moins 2 mois de DSN consécutifs pour détecter les augmentations.
        Avec un seul fichier DSN, cet indicateur ne peut pas être calculé.

        Barème officiel (sur 20 points):
        - Écart ≤ 2% : 20 points
        - Écart de 3% : 10 points
        - Écart de 4% : 5 points
        - Écart ≥ 5% : 0 points

        Returns:
            Dictionnaire avec le détail du calcul et le score
        """
        return {
            'score': None,
            'score_max': 20,
            'calculable': False,
            'message': "Nécessite plusieurs mois de DSN consécutifs pour détecter les augmentations individuelles",
            'explication': (
                "Pour calculer cet indicateur, il faut comparer les rémunérations entre "
                "deux périodes (exemple : janvier vs décembre de l'année précédente). "
                "Uploadez plusieurs fichiers DSN mensuels pour activer ce calcul."
            ),
            'augmentations_hommes': 0,
            'augmentations_femmes': 0,
            'taux_hommes': 0,
            'taux_femmes': 0,
            'ecart': 0
        }

    def calculer_indicateur_promotions(self, types_filtres: list = None) -> Dict[str, Any]:
        """
        Calcule l'Indicateur 3 - Écart de taux de promotions

        ATTENTION: Nécessite au moins 2 mois de DSN consécutifs pour détecter les promotions.
        Avec un seul fichier DSN, cet indicateur ne peut pas être calculé.

        Barème officiel (sur 15 points):
        - Écart ≤ 2% : 15 points
        - Écart de 3% : 10 points
        - Écart de 4% : 5 points
        - Écart ≥ 5% : 0 points

        Returns:
            Dictionnaire avec le détail du calcul et le score
        """
        return {
            'score': None,
            'score_max': 15,
            'calculable': False,
            'message': "Nécessite plusieurs mois de DSN consécutifs pour détecter les promotions",
            'explication': (
                "Pour calculer cet indicateur, il faut détecter les changements de CSP "
                "(Catégorie Socio-Professionnelle) entre deux périodes. "
                "Uploadez plusieurs fichiers DSN mensuels pour activer ce calcul."
            ),
            'promotions_hommes': 0,
            'promotions_femmes': 0,
            'taux_hommes': 0,
            'taux_femmes': 0,
            'ecart': 0
        }

    def calculer_indicateur_conge_maternite(self, types_filtres: list = None) -> Dict[str, Any]:
        """
        Calcule l'Indicateur 4 - Pourcentage de salariées augmentées au retour de congé maternité

        ATTENTION: Nécessite plusieurs mois de DSN et les données d'arrêts de travail (S21.G00.60).

        Barème officiel (sur 15 points):
        - 100% des salariées augmentées = 15 points
        - Proportionnel en dessous

        Returns:
            Dictionnaire avec le détail du calcul et le score
        """
        return {
            'score': None,
            'score_max': 15,
            'calculable': False,
            'message': "Nécessite plusieurs mois de DSN et les données d'arrêts de travail (congé maternité)",
            'explication': (
                "Pour calculer cet indicateur, il faut identifier les congés maternité "
                "(bloc S21.G00.60 avec motif '11') et vérifier si les salariées ont eu "
                "une augmentation dans l'année suivant leur retour. "
                "Le fichier DSN actuel ne contient pas de données d'arrêts de travail."
            ),
            'nb_retours_conge': 0,
            'nb_augmentees': 0,
            'pourcentage': 0
        }

    def calculer_indicateur_top10(self, types_filtres: list = None) -> Dict[str, Any]:
        """
        Calcule l'Indicateur 5 - Nombre de salariés du sexe sous-représenté
        parmi les 10 plus hautes rémunérations

        Barème officiel (sur 10 points):
        - 4 ou 5 personnes du sexe sous-représenté = 10 points
        - 2 ou 3 personnes = 5 points
        - 0 ou 1 personne = 0 points

        Args:
            types_filtres: Liste des codes de types de rémunération à inclure

        Returns:
            Dictionnaire avec le détail du calcul et le score
        """
        # Calculer la rémunération totale pour chaque salarié
        salaries_avec_remun = []

        for salarie in self.stats['salaries']:
            sexe = salarie.get('sexe')
            if sexe not in ['M', 'F']:
                continue

            # Calculer la rémunération totale (filtrée)
            remunerations = salarie.get('remunerations', [])
            if types_filtres:
                remunerations = [
                    r for r in remunerations
                    if isinstance(r, dict) and r.get('type_code') in types_filtres
                ]

            remun_totale = sum(r['montant'] if isinstance(r, dict) else r for r in remunerations) if remunerations else 0

            if remun_totale > 0:
                salaries_avec_remun.append({
                    'nom': salarie.get('nom', ''),
                    'prenom': salarie.get('prenom', ''),
                    'matricule': salarie.get('matricule', ''),
                    'sexe': sexe,
                    'remuneration': remun_totale,
                    'csp': salarie.get('csp', '')
                })

        # Trier par rémunération décroissante et prendre les 10 premiers
        top10 = sorted(salaries_avec_remun, key=lambda x: x['remuneration'], reverse=True)[:10]

        if len(top10) < 10:
            return {
                'score': 0,
                'score_max': 10,
                'top10': top10,
                'nb_hommes': 0,
                'nb_femmes': 0,
                'sexe_sous_represente': None,
                'nb_sexe_sous_represente': 0,
                'message': f"Moins de 10 salariés avec rémunération ({len(top10)} trouvés). Indicateur non calculable."
            }

        # Compter hommes et femmes dans le top 10
        nb_hommes = sum(1 for s in top10 if s['sexe'] == 'M')
        nb_femmes = sum(1 for s in top10 if s['sexe'] == 'F')

        # Déterminer le sexe sous-représenté (dans l'entreprise globale, pas dans le top10)
        total_hommes = sum(1 for s in self.stats['salaries'] if s.get('sexe') == 'M')
        total_femmes = sum(1 for s in self.stats['salaries'] if s.get('sexe') == 'F')

        if total_femmes < total_hommes:
            sexe_sous_represente = 'F'
            nb_sexe_sous_represente = nb_femmes
        else:
            sexe_sous_represente = 'M'
            nb_sexe_sous_represente = nb_hommes

        # Calcul du score selon le barème officiel
        if nb_sexe_sous_represente >= 4:
            score = 10
        elif nb_sexe_sous_represente >= 2:
            score = 5
        else:
            score = 0

        return {
            'score': score,
            'score_max': 10,
            'top10': top10,
            'nb_hommes': nb_hommes,
            'nb_femmes': nb_femmes,
            'sexe_sous_represente': 'Femmes' if sexe_sous_represente == 'F' else 'Hommes',
            'nb_sexe_sous_represente': nb_sexe_sous_represente,
            'total_entreprise_hommes': total_hommes,
            'total_entreprise_femmes': total_femmes,
            'message': None
        }

    def calculer_egalite_hf(self, types_filtres: list = None) -> Dict[str, Any]:
        """
        Calcule les statistiques d'égalité homme-femme

        Args:
            types_filtres: Liste des codes de types de rémunération à inclure (ex: ['001', '010'])
                          Si None, tous les types sont inclus
        """
        total_h = 0
        total_f = 0
        remun_h = []
        remun_f = []

        for salarie in self.stats['salaries']:
            sexe = salarie.get('sexe')
            remunerations = salarie.get('remunerations', [])

            # Filtrer les rémunérations selon les types sélectionnés
            if types_filtres:
                remunerations = [
                    r for r in remunerations
                    if isinstance(r, dict) and r.get('type_code') in types_filtres
                ]

            # Les rémunérations sont maintenant des objets avec 'montant', 'date_debut', 'date_fin'
            remun_totale = sum(r['montant'] if isinstance(r, dict) else r for r in remunerations) if remunerations else 0

            if sexe == 'M':
                total_h += 1
                if remun_totale > 0:
                    remun_h.append(remun_totale)
            elif sexe == 'F':
                total_f += 1
                if remun_totale > 0:
                    remun_f.append(remun_totale)

        # Calcul des moyennes
        moyenne_h = sum(remun_h) / len(remun_h) if remun_h else 0
        moyenne_f = sum(remun_f) / len(remun_f) if remun_f else 0

        # Calcul de l'écart (en %)
        ecart = 0
        if moyenne_h > 0:
            ecart = ((moyenne_h - moyenne_f) / moyenne_h) * 100

        return {
            'total_salaries': total_h + total_f,
            'hommes': total_h,
            'femmes': total_f,
            'pourcentage_h': round((total_h / (total_h + total_f) * 100), 2) if (total_h + total_f) > 0 else 0,
            'pourcentage_f': round((total_f / (total_h + total_f) * 100), 2) if (total_h + total_f) > 0 else 0,
            'remuneration_moyenne_h': round(moyenne_h, 2),
            'remuneration_moyenne_f': round(moyenne_f, 2),
            'ecart_remuneration': round(ecart, 2),
            'nb_avec_remuneration_h': len(remun_h),
            'nb_avec_remuneration_f': len(remun_f)
        }

    def recalculer_tranches_age(self, date_reference: str = None):
        """
        Recalcule les tranches d'âge de tous les salariés avec une date de référence

        Args:
            date_reference: Date de référence au format DDMMYYYY (par défaut: date de fin de période DSN)
        """
        # Utiliser la date de référence fournie, sinon celle extraite du fichier, sinon la date du jour
        date_ref = date_reference or self.date_reference

        for salarie in self.stats['salaries']:
            date_naissance = salarie.get('date_naissance')
            if date_naissance:
                salarie['tranche_age'] = self._calculate_age_group(date_naissance, date_ref)

    def _calculer_indicateur_augmentations_multi_mois(self, parsers_list: list,
                                                       types_filtres: list = None) -> Dict[str, Any]:
        """
        Calcule l'Indicateur 2 - Écart de taux d'augmentations individuelles (mode multi-mois)

        Compare le premier et le dernier mois pour détecter les augmentations de salaire.
        Une augmentation est détectée si le salaire du dernier mois > salaire du premier mois + 5%

        Barème: écart ≤ 2% = 20 pts, ≤ 3% = 10 pts, ≤ 5% = 5 pts, > 5% = 0 pts
        """
        if len(parsers_list) < 2:
            return {
                'score': None,
                'score_max': 20,
                'calculable': False,
                'message': "Nécessite au moins 2 mois de DSN pour détecter les augmentations"
            }

        parser_debut = parsers_list[0]
        parser_fin = parsers_list[-1]

        # Construire un dictionnaire matricule -> rémunération pour chaque période
        salaires_debut = {}
        for salarie in parser_debut.stats['salaries']:
            matricule = salarie.get('matricule')
            sexe = salarie.get('sexe')
            csp = salarie.get('csp')
            if matricule and sexe in ['M', 'F']:
                remunerations = salarie.get('remunerations', [])
                if types_filtres:
                    remunerations = [r for r in remunerations
                                   if isinstance(r, dict) and r.get('type_code') in types_filtres]
                total = sum(r['montant'] if isinstance(r, dict) else r for r in remunerations)
                salaires_debut[matricule] = {'salaire': total, 'sexe': sexe, 'csp': csp}

        salaires_fin = {}
        for salarie in parser_fin.stats['salaries']:
            matricule = salarie.get('matricule')
            sexe = salarie.get('sexe')
            csp = salarie.get('csp')
            if matricule and sexe in ['M', 'F']:
                remunerations = salarie.get('remunerations', [])
                if types_filtres:
                    remunerations = [r for r in remunerations
                                   if isinstance(r, dict) and r.get('type_code') in types_filtres]
                total = sum(r['montant'] if isinstance(r, dict) else r for r in remunerations)
                salaires_fin[matricule] = {'salaire': total, 'sexe': sexe, 'csp': csp}

        # Détecter les augmentations (salaire fin > salaire début * 1.05)
        augmentations = {'M': 0, 'F': 0}
        effectifs = {'M': 0, 'F': 0}

        for matricule, data_debut in salaires_debut.items():
            if matricule in salaires_fin:
                data_fin = salaires_fin[matricule]
                if data_debut['salaire'] > 0 and data_fin['salaire'] > 0:
                    sexe = data_debut['sexe']
                    effectifs[sexe] += 1
                    # Augmentation détectée si +5% ou plus
                    if data_fin['salaire'] > data_debut['salaire'] * 1.05:
                        augmentations[sexe] += 1

        # Calculer les taux d'augmentation par sexe
        taux_h = (augmentations['M'] / effectifs['M'] * 100) if effectifs['M'] > 0 else 0
        taux_f = (augmentations['F'] / effectifs['F'] * 100) if effectifs['F'] > 0 else 0
        ecart = abs(taux_h - taux_f)

        # Barème officiel
        if ecart <= 2:
            score = 20
        elif ecart <= 3:
            score = 10
        elif ecart <= 5:
            score = 5
        else:
            score = 0

        return {
            'score': score,
            'score_max': 20,
            'calculable': True,
            'taux_augmentation_hommes': round(taux_h, 2),
            'taux_augmentation_femmes': round(taux_f, 2),
            'ecart': round(ecart, 2),
            'nb_augmentations_hommes': augmentations['M'],
            'nb_augmentations_femmes': augmentations['F'],
            'effectif_hommes': effectifs['M'],
            'effectif_femmes': effectifs['F'],
            'periode_comparaison': f"{parser_debut.current_period.get('date_fin', 'N/A')} → {parser_fin.current_period.get('date_fin', 'N/A')}"
        }

    def _calculer_indicateur_promotions_multi_mois(self, parsers_list: list,
                                                    types_filtres: list = None) -> Dict[str, Any]:
        """
        Calcule l'Indicateur 3 - Écart de taux de promotions (mode multi-mois)

        Détecte les changements de CSP (catégorie socio-professionnelle) entre premier et dernier mois.

        Barème: écart ≤ 2% = 15 pts, ≤ 3% = 10 pts, ≤ 5% = 5 pts, > 5% = 0 pts
        """
        if len(parsers_list) < 2:
            return {
                'score': None,
                'score_max': 15,
                'calculable': False,
                'message': "Nécessite au moins 2 mois de DSN pour détecter les promotions"
            }

        parser_debut = parsers_list[0]
        parser_fin = parsers_list[-1]

        # Construire un dictionnaire matricule -> CSP pour chaque période
        csp_debut = {}
        for salarie in parser_debut.stats['salaries']:
            matricule = salarie.get('matricule')
            sexe = salarie.get('sexe')
            csp = salarie.get('csp')
            if matricule and sexe in ['M', 'F'] and csp:
                csp_debut[matricule] = {'csp': csp, 'sexe': sexe}

        csp_fin = {}
        for salarie in parser_fin.stats['salaries']:
            matricule = salarie.get('matricule')
            sexe = salarie.get('sexe')
            csp = salarie.get('csp')
            if matricule and sexe in ['M', 'F'] and csp:
                csp_fin[matricule] = {'csp': csp, 'sexe': sexe}

        # Hiérarchie CSP (du plus bas au plus haut)
        hierarchie_csp = {
            '5': 1,  # Ouvriers
            '4': 2,  # Employés
            '3': 3,  # Professions intermédiaires
            '2': 4,  # Cadres
            '1': 5   # Cadres dirigeants
        }

        # Détecter les promotions (changement de CSP vers le haut)
        promotions = {'M': 0, 'F': 0}
        effectifs = {'M': 0, 'F': 0}

        for matricule, data_debut in csp_debut.items():
            if matricule in csp_fin:
                data_fin = csp_fin[matricule]
                sexe = data_debut['sexe']
                effectifs[sexe] += 1

                csp_d = data_debut['csp']
                csp_f = data_fin['csp']

                # Promotion si CSP fin > CSP début dans la hiérarchie
                if (csp_d in hierarchie_csp and csp_f in hierarchie_csp and
                    hierarchie_csp[csp_f] > hierarchie_csp[csp_d]):
                    promotions[sexe] += 1

        # Calculer les taux de promotion par sexe
        taux_h = (promotions['M'] / effectifs['M'] * 100) if effectifs['M'] > 0 else 0
        taux_f = (promotions['F'] / effectifs['F'] * 100) if effectifs['F'] > 0 else 0
        ecart = abs(taux_h - taux_f)

        # Barème officiel
        if ecart <= 2:
            score = 15
        elif ecart <= 3:
            score = 10
        elif ecart <= 5:
            score = 5
        else:
            score = 0

        return {
            'score': score,
            'score_max': 15,
            'calculable': True,
            'taux_promotion_hommes': round(taux_h, 2),
            'taux_promotion_femmes': round(taux_f, 2),
            'ecart': round(ecart, 2),
            'nb_promotions_hommes': promotions['M'],
            'nb_promotions_femmes': promotions['F'],
            'effectif_hommes': effectifs['M'],
            'effectif_femmes': effectifs['F'],
            'periode_comparaison': f"{parser_debut.current_period.get('date_fin', 'N/A')} → {parser_fin.current_period.get('date_fin', 'N/A')}"
        }

    def _calculer_indicateur_conge_maternite_multi_mois(self, parsers_list: list,
                                                         types_filtres: list = None) -> Dict[str, Any]:
        """
        Calcule l'Indicateur 4 - % de salariées augmentées au retour de congé maternité

        ATTENTION: Nécessite les données d'arrêts de travail (S21.G00.60) pour détecter les congés maternité.
        Pour l'instant, cette fonction retourne "non calculable" car ces données ne sont généralement pas
        présentes dans les DSN standards.

        Barème: 100% augmentées = 15 pts, sinon 0 pts
        """
        return {
            'score': None,
            'score_max': 15,
            'calculable': False,
            'message': "Nécessite les données d'arrêts de travail (S21.G00.60 - congés maternité)",
            'explication': (
                "Cet indicateur nécessite de détecter les congés maternité via les arrêts de travail "
                "(bloc S21.G00.60 avec motif congé maternité), puis de vérifier si les salariées concernées "
                "ont bénéficié d'une augmentation dans l'année suivant leur retour. "
                "Ces données ne sont pas systématiquement présentes dans les DSN."
            )
        }

    def get_results(self, types_filtres: list = None, date_reference: str = None) -> Dict[str, Any]:
        """
        Retourne les résultats de l'analyse

        Args:
            types_filtres: Liste des codes de types de rémunération à inclure
            date_reference: Date de référence pour le calcul de l'âge (format DDMMYYYY)
        """
        # Recalculer les tranches d'âge avec la date de référence
        self.recalculer_tranches_age(date_reference)

        egalite = self.calculer_egalite_hf(types_filtres)
        index_officiel = self.calculer_index_officiel(types_filtres)
        indicateur_augmentations = self.calculer_indicateur_augmentations(types_filtres)
        indicateur_promotions = self.calculer_indicateur_promotions(types_filtres)
        indicateur_conge_maternite = self.calculer_indicateur_conge_maternite(types_filtres)
        indicateur_top10 = self.calculer_indicateur_top10(types_filtres)

        # Extraire tous les types de rémunération trouvés dans le fichier
        types_trouves = set()
        for salarie in self.stats['salaries']:
            for remun in salarie.get('remunerations', []):
                if isinstance(remun, dict) and remun.get('type_code'):
                    types_trouves.add(remun['type_code'])

        # Créer une liste des types avec leurs libellés
        types_disponibles = [
            {
                'code': code,
                'libelle': self.TYPES_REMUNERATION.get(code, f'Type {code}')
            }
            for code in sorted(types_trouves)
        ]

        return {
            'stats': self.stats,
            'blocks': dict(self.blocks),
            'raw_lines': self.raw_lines[:100],  # Limite aux 100 premières lignes
            'summary': {
                'total_lines': self.stats['total_lines'],
                'nb_blocks': len(self.blocks),
                'nb_salaries': len(self.stats['salaries']),
                'entreprise': self.stats['entreprise']
            },
            'egalite_hf': egalite,
            'index_officiel': index_officiel,
            'indicateur_augmentations': indicateur_augmentations,
            'indicateur_promotions': indicateur_promotions,
            'indicateur_conge_maternite': indicateur_conge_maternite,
            'indicateur_top10': indicateur_top10,
            'types_disponibles': types_disponibles,
            'date_reference': date_reference or self.date_reference
        }

    def get_results_multi_mois(self, parsers_list: list, types_filtres: list = None,
                                date_reference: str = None) -> Dict[str, Any]:
        """
        Obtient les résultats de l'analyse en mode multi-mois (comparaison entre plusieurs DSN)

        Args:
            parsers_list: Liste des objets DSNParser (un par mois)
            types_filtres: Liste des codes de types de rémunération à inclure
            date_reference: Date de référence pour le calcul de l'âge (format DDMMYYYY)

        Returns:
            Dictionnaire avec les résultats incluant les indicateurs 2, 3, 4
        """
        # Trier les parsers par date de période (du plus ancien au plus récent)
        parsers_list = sorted(parsers_list, key=lambda p: p.current_period.get('date_fin', ''))

        # Utiliser le dernier parser comme référence pour les stats de base
        parser_dernier = parsers_list[-1]
        parser_dernier.recalculer_tranches_age(date_reference)

        # Calculer les indicateurs classiques (1 et 5) sur le dernier mois
        egalite = parser_dernier.calculer_egalite_hf(types_filtres)
        index_officiel = parser_dernier.calculer_index_officiel(types_filtres)
        indicateur_top10 = parser_dernier.calculer_indicateur_top10(types_filtres)

        # Calculer les indicateurs multi-mois (2, 3, 4)
        indicateur_augmentations = self._calculer_indicateur_augmentations_multi_mois(
            parsers_list, types_filtres
        )
        indicateur_promotions = self._calculer_indicateur_promotions_multi_mois(
            parsers_list, types_filtres
        )
        indicateur_conge_maternite = self._calculer_indicateur_conge_maternite_multi_mois(
            parsers_list, types_filtres
        )

        # Extraire tous les types de rémunération trouvés
        types_trouves = set()
        for salarie in parser_dernier.stats['salaries']:
            for remun in salarie.get('remunerations', []):
                if isinstance(remun, dict) and remun.get('type_code'):
                    types_trouves.add(remun['type_code'])

        types_disponibles = [
            {
                'code': code,
                'libelle': self.TYPES_REMUNERATION.get(code, f'Type {code}')
            }
            for code in sorted(types_trouves)
        ]

        return {
            'stats': parser_dernier.stats,
            'blocks': dict(parser_dernier.blocks),
            'raw_lines': parser_dernier.raw_lines[:100],
            'summary': {
                'total_lines': parser_dernier.stats['total_lines'],
                'nb_blocks': len(parser_dernier.blocks),
                'nb_salaries': len(parser_dernier.stats['salaries']),
                'entreprise': parser_dernier.stats['entreprise'],
                'nb_mois_analyses': len(parsers_list),
                'periode_analyse': f"{parsers_list[0].current_period.get('date_fin', 'N/A')} à {parsers_list[-1].current_period.get('date_fin', 'N/A')}"
            },
            'egalite_hf': egalite,
            'index_officiel': index_officiel,
            'indicateur_augmentations': indicateur_augmentations,
            'indicateur_promotions': indicateur_promotions,
            'indicateur_conge_maternite': indicateur_conge_maternite,
            'indicateur_top10': indicateur_top10,
            'types_disponibles': types_disponibles,
            'date_reference': date_reference or parser_dernier.date_reference
        }

    def to_dataframe(self):
        """Convertit les données en DataFrame pandas"""
        import pandas as pd

        data = []
        for rubrique, entries in self.blocks.items():
            for entry in entries:
                data.append({
                    'Rubrique': rubrique,
                    'Valeur': entry['valeur']
                })

        return pd.DataFrame(data)


def analyze_dsn_file(file_path: str) -> Dict[str, Any]:
    """
    Fonction helper pour analyser un fichier DSN

    Args:
        file_path: Chemin vers le fichier DSN

    Returns:
        Dictionnaire avec les résultats de l'analyse
    """
    parser = DSNParser()
    return parser.parse_file(file_path)
