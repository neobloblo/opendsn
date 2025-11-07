"""
Application Flask DSN - Gestion de la norme DSN
"""
from flask import Flask, render_template, request
import sqlite3
import pandas as pd
import os

app = Flask(__name__)

# Créer le dossier uploads au démarrage si inexistant
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    import sys
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    print(f"✅ Dossier '{UPLOAD_FOLDER}/' créé")

def get_db_connection():
    """Connexion à la base de données SQLite"""
    conn = sqlite3.connect('dsn.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def accueil():
    """Page d'accueil"""
    return render_template('accueil.html')

@app.route('/structures')
def structures():
    """Page des structures hiérarchiques DSN"""
    conn = get_db_connection()
    df = pd.read_sql_query(
        "SELECT ordre, code, nom, description FROM structures ORDER BY ordre",
        conn
    )
    conn.close()

    structures = df.to_dict('records')
    return render_template('structures.html', structures=structures)

@app.route('/rubriques')
def rubriques():
    """Page des rubriques DSN avec filtre par structure et groupées par sous-groupe"""
    conn = get_db_connection()

    # Récupérer le filtre de structure depuis l'URL (ex: ?structure=S10)
    structure_filter = request.args.get('structure', 'S10')  # Par défaut S10

    # Récupérer toutes les structures pour le sélecteur
    structures_df = pd.read_sql_query(
        "SELECT code, nom FROM structures ORDER BY ordre",
        conn
    )
    structures_list = structures_df.to_dict('records')

    # Récupérer les sous-groupes pour la structure sélectionnée
    sous_groupes_df = pd.read_sql_query(
        "SELECT code, nom, cardinalite FROM sous_groupes "
        "WHERE structure_code = ? ORDER BY code",
        conn,
        params=[structure_filter]
    )

    # Pour chaque sous-groupe, récupérer ses rubriques
    sous_groupes_avec_rubriques = []
    for _, sg in sous_groupes_df.iterrows():
        rubriques_df = pd.read_sql_query(
            "SELECT code, nom, description, type_donnee, taille_max, obligatoire, format "
            "FROM rubriques WHERE sous_groupe_code = ? ORDER BY code",
            conn,
            params=[sg['code']]
        )

        sous_groupes_avec_rubriques.append({
            'code': sg['code'],
            'nom': sg['nom'],
            'cardinalite': sg['cardinalite'],
            'rubriques': rubriques_df.to_dict('records')
        })

    conn.close()

    return render_template('rubriques.html',
                         sous_groupes=sous_groupes_avec_rubriques,
                         structures=structures_list,
                         structure_selectionnee=structure_filter)

@app.route('/categories-socioprofessionnelles')
def categories_socioprofessionnelles():
    """Page des catégories socioprofessionnelles"""
    conn = get_db_connection()

    # Définir les groupes de CSP (premier chiffre du code PCS-ESE)
    groupes = [
        {'code': '2', 'libelle': 'Artisans, commerçants et chefs d\'entreprise', 'code_interne': '25'},
        {'code': '3', 'libelle': 'Cadres et professions intellectuelles supérieures', 'code_interne': '24'},
        {'code': '4', 'libelle': 'Professions intermédiaires', 'code_interne': '23'},
        {'code': '5', 'libelle': 'Employés', 'code_interne': '22'},
        {'code': '6', 'libelle': 'Ouvriers', 'code_interne': '21'}
    ]

    # Récupérer toute la nomenclature PCS-ESE depuis la base de données
    try:
        nomenclature_df = pd.read_sql_query(
            "SELECT code, libelle, categorie_principale FROM nomenclature_pcs_ese ORDER BY code",
            conn
        )
        nomenclature_complete = nomenclature_df.to_dict('records')

        # Regrouper par catégorie principale (premier chiffre)
        nomenclature_par_groupe = {}
        for item in nomenclature_complete:
            groupe_code = str(item['categorie_principale'])
            if groupe_code not in nomenclature_par_groupe:
                nomenclature_par_groupe[groupe_code] = []
            nomenclature_par_groupe[groupe_code].append(item)

        # Extraire les CSP uniques (2 premiers chiffres)
        csp_uniques = {}
        for item in nomenclature_complete:
            code_pcs = item['code']
            if len(code_pcs) >= 2:
                csp_code = code_pcs[0:2]
                if csp_code not in csp_uniques:
                    csp_uniques[csp_code] = {
                        'code': csp_code,
                        'libelle': item['libelle'],
                        'groupe': str(item['categorie_principale'])
                    }

        csp_liste = sorted(csp_uniques.values(), key=lambda x: x['code'])

    except Exception as e:
        nomenclature_complete = []
        nomenclature_par_groupe = {}
        csp_liste = []
        print(f"Erreur lors du chargement de la nomenclature: {e}")

    conn.close()

    return render_template('categories_socioprofessionnelles.html',
                         groupes=groupes,
                         nomenclature_par_groupe=nomenclature_par_groupe,
                         csp_liste=csp_liste,
                         nomenclature_complete=nomenclature_complete)

@app.route('/analyse')
def analyse():
    """Page d'analyse DSN"""
    return render_template('analyse.html')

@app.route('/egalite-hf', methods=['GET', 'POST'])
def egalite_hf():
    """Page indicateur égalité homme-femme"""
    import os
    from dsn_parser import DSNParser

    upload_success = False
    upload_error = None
    files_info = []
    analyse_data = None
    upload_folder = 'uploads'

    if request.method == 'POST':
        # Vérifier si on doit garder des fichiers déjà uploadés
        keep_files = request.form.getlist('keep_files')

        if keep_files:
            # Recalculer avec les fichiers existants
            for keep_file in keep_files:
                filepath = os.path.join(upload_folder, keep_file)
                if os.path.exists(filepath):
                    file_size = os.path.getsize(filepath)
                    files_info.append({
                        'filename': keep_file,
                        'size': f"{file_size / 1024:.2f} KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.2f} MB",
                        'path': filepath
                    })
                else:
                    upload_error = f"Le fichier {keep_file} n'existe plus"
        elif 'dsn_files' not in request.files:
            upload_error = "Aucun fichier sélectionné"
        else:
            files = request.files.getlist('dsn_files')
            if not files or files[0].filename == '':
                upload_error = "Aucun fichier sélectionné"
            elif len(files) > 12:
                upload_error = "Vous ne pouvez uploader que 12 fichiers maximum"
            else:
                # Sauvegarder les fichiers
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

                for file in files:
                    if file.filename:
                        filepath = os.path.join(upload_folder, file.filename)
                        file.save(filepath)

                        # Récupérer les infos du fichier
                        file_size = os.path.getsize(filepath)
                        files_info.append({
                            'filename': file.filename,
                            'size': f"{file_size / 1024:.2f} KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.2f} MB",
                            'path': filepath
                        })

        # Si on a des fichiers (nouveaux ou existants), les analyser
        if files_info and not upload_error:
            # Récupérer les types de rémunération sélectionnés (par défaut '003' - Salaire rétabli)
            types_selectionnes = request.form.getlist('types_remuneration')
            if not types_selectionnes:
                types_selectionnes = ['003']  # Par défaut: Salaire rétabli - reconstitué

            # Récupérer la date de référence depuis le formulaire (format YYYY-MM-DD)
            date_reference_html = request.form.get('date_reference', '')

            # Convertir au format DSN (DDMMYYYY)
            date_reference = None
            if date_reference_html:
                try:
                    from datetime import datetime
                    dt = datetime.strptime(date_reference_html, '%Y-%m-%d')
                    date_reference = dt.strftime('%d%m%Y')
                except:
                    pass

            # Analyser les fichiers DSN
            try:
                # Parser pour chaque fichier
                parsers = []
                for file_info in files_info:
                    parser = DSNParser()
                    parser.parse_file(file_info['path'])
                    parsers.append(parser)

                # Si un seul fichier, utiliser le mode classique
                if len(parsers) == 1:
                    analyse_data = parsers[0].get_results(
                        types_filtres=types_selectionnes,
                        date_reference=date_reference
                    )
                else:
                    # Mode multi-mois : analyser les données comparatives
                    analyse_data = parsers[0].get_results_multi_mois(
                        parsers_list=parsers,
                        types_filtres=types_selectionnes,
                        date_reference=date_reference
                    )

                upload_success = True
            except Exception as e:
                import traceback
                traceback.print_exc()
                upload_error = f"Erreur lors de l'analyse des fichiers : {str(e)}"

    # Récupérer les types sélectionnés et la date de référence pour les passer au template
    types_selectionnes = request.form.getlist('types_remuneration') if request.method == 'POST' else ['003']
    if not types_selectionnes:
        types_selectionnes = ['003']

    date_reference_form = request.form.get('date_reference', '') if request.method == 'POST' else ''

    return render_template('egalite_hf.html',
                         upload_success=upload_success,
                         upload_error=upload_error,
                         files_info=files_info,
                         analyse=analyse_data,
                         types_selectionnes=types_selectionnes,
                         date_reference_form=date_reference_form)

@app.route('/evolution-effectif', methods=['GET', 'POST'])
def evolution_effectif():
    """Page d'évolution de l'effectif"""
    import os
    from dsn_parser import DSNParser
    from datetime import datetime
    from collections import defaultdict

    upload_success = False
    upload_error = None
    files_info = []
    evolution_data = None
    upload_folder = 'uploads'

    if request.method == 'POST':
        # Vérifier si on doit garder des fichiers déjà uploadés
        keep_files = request.form.getlist('keep_files')

        if keep_files:
            # Recalculer avec les fichiers existants
            for keep_file in keep_files:
                filepath = os.path.join(upload_folder, keep_file)
                if os.path.exists(filepath):
                    file_size = os.path.getsize(filepath)
                    files_info.append({
                        'filename': keep_file,
                        'size': f"{file_size / 1024:.2f} KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.2f} MB",
                        'path': filepath
                    })
                else:
                    upload_error = f"Le fichier {keep_file} n'existe plus"
        elif 'dsn_files' not in request.files:
            upload_error = "Aucun fichier sélectionné"
        else:
            files = request.files.getlist('dsn_files')
            if not files or files[0].filename == '':
                upload_error = "Aucun fichier sélectionné"
            elif len(files) > 24:
                upload_error = "Vous ne pouvez uploader que 24 fichiers maximum"
            else:
                # Sauvegarder les fichiers
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

                for file in files:
                    if file.filename:
                        filepath = os.path.join(upload_folder, file.filename)
                        file.save(filepath)

                        # Récupérer les infos du fichier
                        file_size = os.path.getsize(filepath)
                        files_info.append({
                            'filename': file.filename,
                            'size': f"{file_size / 1024:.2f} KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.2f} MB",
                            'path': filepath
                        })

        # Si on a des fichiers (nouveaux ou existants), les analyser
        if files_info and not upload_error:
            try:
                # Fonction pour convertir la date DSN en libellé
                def format_date_dsn(date_str):
                    """Convertit une date DSN (01MMYYYY) en 'MOIS ANNEE'"""
                    if not date_str or len(date_str) != 8:
                        return "Date invalide"
                    mois_names = {
                        '01': 'JANVIER', '02': 'FÉVRIER', '03': 'MARS',
                        '04': 'AVRIL', '05': 'MAI', '06': 'JUIN',
                        '07': 'JUILLET', '08': 'AOÛT', '09': 'SEPTEMBRE',
                        '10': 'OCTOBRE', '11': 'NOVEMBRE', '12': 'DÉCEMBRE'
                    }
                    mois = date_str[2:4]
                    annee = date_str[4:8]
                    return f"{mois_names.get(mois, mois)} {annee}"

                # Parser chaque fichier et extraire les dates
                files_data = []
                for file_info in files_info:
                    parser = DSNParser()
                    parser.parse_file(file_info['path'])

                    date_declaration = parser.date_declaration or ""

                    # Créer une clé de tri au format YYYYMM pour trier par année puis par mois
                    # Format date_declaration: "01MMYYYY" (ex: "01012024")
                    if date_declaration and len(date_declaration) == 8:
                        annee = date_declaration[4:8]  # YYYY
                        mois = date_declaration[2:4]   # MM
                        date_sort_key = annee + mois   # YYYYMM (ex: "202401")
                    else:
                        date_sort_key = '999999'  # Valeur par défaut si pas de date

                    files_data.append({
                        'parser': parser,
                        'filename': file_info['filename'],
                        'size': file_info['size'],
                        'path': file_info['path'],
                        'date_declaration': date_declaration,
                        'date_sort_key': date_sort_key  # Pour le tri au format YYYYMM
                    })

                # Trier les fichiers par date de déclaration (année puis mois)
                files_data.sort(key=lambda x: x['date_sort_key'])

                # Calculer la longueur maximale des labels de date pour l'alignement
                max_date_length = 0
                for file_data in files_data:
                    if file_data['date_declaration']:
                        date_label = format_date_dsn(file_data['date_declaration'])
                        max_date_length = max(max_date_length, len(date_label))

                # Mettre à jour files_info avec les données triées et formatées
                files_info_sorted = []
                parsers = []
                mois_labels = []
                periodes = []  # Liste des périodes seules (MOIS ANNEE)
                for file_data in files_data:
                    parsers.append(file_data['parser'])

                    # Formater le label pour l'affichage avec alignement
                    if file_data['date_declaration']:
                        date_label = format_date_dsn(file_data['date_declaration'])
                        # Ajouter des espaces pour aligner les ":"
                        padding = ' ' * (max_date_length - len(date_label))
                        label = f"DSN {date_label}{padding} : {file_data['filename']}"
                        display_label = f"{date_label}{padding} : {file_data['filename']}"
                        periodes.append(date_label)  # Stocker uniquement la période
                    else:
                        label = f"DSN : {file_data['filename']}"
                        display_label = file_data['filename']
                        periodes.append(file_data['filename'])  # Fallback si pas de date

                    mois_labels.append(label)
                    files_info_sorted.append({
                        'filename': file_data['filename'],
                        'size': file_data['size'],
                        'path': file_data['path'],
                        'display_label': display_label
                    })

                # Remplacer files_info par la version triée et formatée
                files_info = files_info_sorted

                # Calculer l'évolution de l'effectif
                evolution_data = {
                    'mois': [],
                    'periodes': [],  # Périodes seules (MOIS ANNEE)
                    'effectif_total': [],
                    'effectif_hommes': [],
                    'effectif_femmes': [],
                    'par_groupe': defaultdict(list),  # Répartition par groupe de CSP (21-26)
                    'entrees': [],
                    'sorties': [],
                    'entrees_details': [],  # Détails des entrées (nom, prénom, date d'embauche)
                    'sorties_details': [],  # Détails des sorties (nom, prénom)
                    'age_moyen': [],  # Âge moyen global par mois
                    'age_moyen_hommes': [],  # Âge moyen des hommes par mois
                    'age_moyen_femmes': [],  # Âge moyen des femmes par mois
                    'salaries_details': [],  # Détails complets de tous les salariés par période
                    'fichiers': [f['filename'] for f in files_info]
                }

                # Fonction pour vérifier si une date (DDMMYYYY) correspond au mois de la déclaration (01MMYYYY)
                def date_dans_mois(date_ddmmyyyy, date_declaration):
                    """Vérifie si une date DDMMYYYY correspond au mois de la date_declaration 01MMYYYY"""
                    if not date_ddmmyyyy or len(date_ddmmyyyy) != 8:
                        return False
                    if not date_declaration or len(date_declaration) != 8:
                        return False

                    # Extraire mois et année
                    mois_date = date_ddmmyyyy[2:4]
                    annee_date = date_ddmmyyyy[4:8]
                    mois_decl = date_declaration[2:4]
                    annee_decl = date_declaration[4:8]

                    return mois_date == mois_decl and annee_date == annee_decl

                for idx, parser in enumerate(parsers):
                    # Récupérer la date de déclaration du mois en cours
                    date_declaration_mois = files_data[idx]['date_declaration']

                    # Compter les salariés actifs ce mois
                    effectif_h = 0
                    effectif_f = 0
                    groupe_count = defaultdict(int)  # Comptage par groupe (21-26)

                    # Listes pour stocker les entrées et sorties du mois
                    entrees_list = []
                    sorties_list = []

                    # Listes pour calculer l'âge moyen par sexe
                    ages_hommes = []
                    ages_femmes = []

                    # Liste pour stocker les détails de tous les salariés de ce mois
                    salaries_mois = []

                    # Calculer la date de référence pour ce mois (dernier jour du mois)
                    if date_declaration_mois and len(date_declaration_mois) == 8:
                        mois_ref = int(date_declaration_mois[2:4])
                        annee_ref = int(date_declaration_mois[4:8])
                        # Dernier jour du mois
                        if mois_ref == 12:
                            dernier_jour_ref = 31
                        elif mois_ref in [4, 6, 9, 11]:
                            dernier_jour_ref = 30
                        elif mois_ref == 2:
                            # Année bissextile
                            if (annee_ref % 4 == 0 and annee_ref % 100 != 0) or (annee_ref % 400 == 0):
                                dernier_jour_ref = 29
                            else:
                                dernier_jour_ref = 28
                        else:
                            dernier_jour_ref = 31
                        date_ref_mois = datetime(annee_ref, mois_ref, dernier_jour_ref)
                    else:
                        date_ref_mois = None

                    if hasattr(parser, 'stats') and 'salaries' in parser.stats:
                        for sal in parser.stats['salaries']:
                            # Utiliser le matricule (S21.G00.30.019) comme identifiant unique
                            matricule = sal.get('matricule', '')
                            nir = sal.get('nir', '')
                            groupe = sal.get('groupe', 'Non renseigné')  # Groupe de CSP (textuel)
                            groupe_code = sal.get('groupe_code', None)  # Code groupe (21-26)
                            csp = sal.get('csp', None)  # Code CSP (2 chiffres)
                            csp_libelle = sal.get('csp_libelle', '')  # Libellé de la CSP
                            date_embauche = sal.get('date_embauche', '')
                            date_sortie = sal.get('date_sortie', '')
                            date_naissance = sal.get('date_naissance', '')

                            # Utiliser le matricule si disponible, sinon le NIR
                            identifiant = matricule if matricule else nir
                            if identifiant:
                                # Déterminer le sexe à partir du premier caractère du NIR
                                sexe = None
                                sexe_libelle = ''
                                if nir and len(nir) > 0:
                                    premier_char = nir[0]
                                    if premier_char == '1':
                                        effectif_h += 1
                                        sexe = 'H'
                                        sexe_libelle = 'Homme'
                                    elif premier_char == '2':
                                        effectif_f += 1
                                        sexe = 'F'
                                        sexe_libelle = 'Femme'

                                # Compter par code groupe numérique (21-26) si disponible
                                if groupe_code:
                                    groupe_count[groupe_code] += 1

                                # Calculer l'âge pour ce mois
                                age_calcule = None
                                if date_naissance and len(date_naissance) == 8 and date_ref_mois and sexe:
                                    try:
                                        jour_naiss = int(date_naissance[0:2])
                                        mois_naiss = int(date_naissance[2:4])
                                        annee_naiss = int(date_naissance[4:8])
                                        date_naiss = datetime(annee_naiss, mois_naiss, jour_naiss)

                                        # Calculer l'âge
                                        age = date_ref_mois.year - date_naiss.year
                                        if (date_ref_mois.month, date_ref_mois.day) < (date_naiss.month, date_naiss.day):
                                            age -= 1

                                        age_calcule = age

                                        if sexe == 'H':
                                            ages_hommes.append(age)
                                        elif sexe == 'F':
                                            ages_femmes.append(age)
                                    except (ValueError, IndexError):
                                        pass

                                # Vérifier si c'est une entrée ce mois
                                est_entree = date_dans_mois(date_embauche, date_declaration_mois)
                                if est_entree:
                                    entrees_list.append({
                                        'nom': sal.get('nom', 'N/A'),
                                        'prenom': sal.get('prenom', 'N/A'),
                                        'date_embauche': date_embauche
                                    })

                                # Vérifier si c'est une sortie ce mois
                                est_sortie = date_dans_mois(date_sortie, date_declaration_mois)
                                if est_sortie:
                                    sorties_list.append({
                                        'nom': sal.get('nom', 'N/A'),
                                        'prenom': sal.get('prenom', 'N/A'),
                                        'date_sortie': date_sortie
                                    })

                                # Ajouter les détails complets du salarié pour ce mois
                                # Mapping des codes groupe vers les libellés
                                groupe_libelle_map = {
                                    '21': 'Ouvriers',
                                    '22': 'Employés',
                                    '23': 'Agents de maîtrise',
                                    '24': 'Cadres',
                                    '25': 'Cadres dirigeants',
                                    '26': 'Autres'
                                }
                                groupe_libelle = groupe_libelle_map.get(groupe_code, groupe)

                                # Récupérer le code emploi (PCS-ESE), le libellé et le statut conventionnel
                                code_emploi = sal.get('code_pcs_ese', '')
                                libelle_emploi = sal.get('libelle_emploi', '')
                                statut_conv = sal.get('statut_conventionnel', '')

                                salaries_mois.append({
                                    'matricule': matricule,
                                    'nir': nir,
                                    'nom': sal.get('nom', ''),
                                    'prenom': sal.get('prenom', ''),
                                    'sexe': sexe_libelle,
                                    'date_naissance': date_naissance,
                                    'age': age_calcule if age_calcule is not None else '',
                                    'groupe': groupe_libelle,  # Groupe de CSP (ex: "Ouvriers")
                                    'groupe_code': groupe_code,  # Code groupe (ex: "21")
                                    'csp': csp,  # Code CSP (2 chiffres, ex: "63")
                                    'csp_libelle': csp_libelle,  # Libellé de la CSP
                                    'code_emploi': code_emploi,
                                    'libelle_emploi': libelle_emploi,
                                    'statut_conventionnel': statut_conv,
                                    'date_embauche': date_embauche,
                                    'date_sortie': date_sortie,
                                    'est_entree': est_entree,
                                    'est_sortie': est_sortie
                                })

                    effectif = effectif_h + effectif_f

                    # Calculer les moyennes d'âge
                    age_moyen_h = int(round(sum(ages_hommes) / len(ages_hommes))) if ages_hommes else 0
                    age_moyen_f = int(round(sum(ages_femmes) / len(ages_femmes))) if ages_femmes else 0
                    # Âge moyen global (tous sexes confondus)
                    ages_tous = ages_hommes + ages_femmes
                    age_moyen_global = int(round(sum(ages_tous) / len(ages_tous))) if ages_tous else 0

                    evolution_data['mois'].append(mois_labels[idx])
                    evolution_data['periodes'].append(periodes[idx])  # Période seule
                    evolution_data['effectif_total'].append(effectif)
                    evolution_data['effectif_hommes'].append(effectif_h)
                    evolution_data['effectif_femmes'].append(effectif_f)
                    evolution_data['entrees_details'].append(entrees_list)
                    evolution_data['sorties_details'].append(sorties_list)
                    evolution_data['entrees'].append(len(entrees_list))
                    evolution_data['sorties'].append(len(sorties_list))
                    evolution_data['age_moyen'].append(age_moyen_global)
                    evolution_data['age_moyen_hommes'].append(age_moyen_h)
                    evolution_data['age_moyen_femmes'].append(age_moyen_f)
                    evolution_data['salaries_details'].append(salaries_mois)

                    # Ajouter les compteurs par groupe de CSP
                    for groupe in ['21', '22', '23', '24', '25', '26']:
                        evolution_data['par_groupe'][groupe].append(groupe_count.get(groupe, 0))

                # Calculer les statistiques globales
                if evolution_data['effectif_total']:
                    evolution_data['stats'] = {
                        'effectif_initial': evolution_data['effectif_total'][0],
                        'effectif_final': evolution_data['effectif_total'][-1],
                        'variation_absolue': evolution_data['effectif_total'][-1] - evolution_data['effectif_total'][0],
                        'variation_pct': ((evolution_data['effectif_total'][-1] - evolution_data['effectif_total'][0]) / evolution_data['effectif_total'][0] * 100) if evolution_data['effectif_total'][0] > 0 else 0,
                        'effectif_moyen': int(round(sum(evolution_data['effectif_total']) / len(evolution_data['effectif_total']))),
                        'total_entrees': sum(evolution_data['entrees']),
                        'total_sorties': sum(evolution_data['sorties'])
                    }

                # Ajouter la date de référence CSP (dernier jour du dernier mois)
                if files_data:
                    derniere_date = files_data[-1]['date_declaration']
                    if derniere_date and len(derniere_date) == 8:
                        mois = int(derniere_date[2:4])
                        annee = int(derniere_date[4:8])
                        # Dernier jour du mois
                        if mois == 12:
                            dernier_jour = 31
                        elif mois in [4, 6, 9, 11]:
                            dernier_jour = 30
                        elif mois == 2:
                            # Année bissextile
                            if (annee % 4 == 0 and annee % 100 != 0) or (annee % 400 == 0):
                                dernier_jour = 29
                            else:
                                dernier_jour = 28
                        else:
                            dernier_jour = 31
                        date_reference_csp = datetime(annee, mois, dernier_jour)
                        evolution_data['date_reference_csp'] = date_reference_csp.strftime('%d/%m/%Y')

                # Calculer la pyramide des âges pour le dernier mois
                if parsers:
                    dernier_parser = parsers[-1]
                    derniere_date = files_data[-1]['date_declaration']

                    # Calculer le dernier jour du mois (date de référence)
                    if derniere_date and len(derniere_date) == 8:
                        mois = int(derniere_date[2:4])
                        annee = int(derniere_date[4:8])
                        # Dernier jour du mois
                        if mois == 12:
                            dernier_jour = 31
                        elif mois in [4, 6, 9, 11]:
                            dernier_jour = 30
                        elif mois == 2:
                            # Année bissextile
                            if (annee % 4 == 0 and annee % 100 != 0) or (annee % 400 == 0):
                                dernier_jour = 29
                            else:
                                dernier_jour = 28
                        else:
                            dernier_jour = 31

                        date_reference = datetime(annee, mois, dernier_jour)
                        date_reference_str = date_reference.strftime('%d/%m/%Y')

                        # Définir les tranches d'âge (du plus élevé au plus faible pour affichage en haut en bas)
                        tranches = ['65+', '60-64', '55-59', '50-54', '45-49', '40-44', '35-39', '30-34', '25-29', '20-24', '<20']
                        pyramide_hommes = {t: 0 for t in tranches}
                        pyramide_femmes = {t: 0 for t in tranches}

                        # Liste pour calculer l'âge moyen
                        ages_list = []

                        # Calculer l'âge de chaque salarié
                        if hasattr(dernier_parser, 'stats') and 'salaries' in dernier_parser.stats:
                            for sal in dernier_parser.stats['salaries']:
                                date_naissance = sal.get('date_naissance', '')
                                nir = sal.get('nir', '')

                                if date_naissance and len(date_naissance) == 8:
                                    try:
                                        jour_naiss = int(date_naissance[0:2])
                                        mois_naiss = int(date_naissance[2:4])
                                        annee_naiss = int(date_naissance[4:8])
                                        date_naiss = datetime(annee_naiss, mois_naiss, jour_naiss)

                                        # Calculer l'âge
                                        age = date_reference.year - date_naiss.year
                                        if (date_reference.month, date_reference.day) < (date_naiss.month, date_naiss.day):
                                            age -= 1

                                        # Ajouter l'âge à la liste pour calculer la moyenne
                                        ages_list.append(age)

                                        # Déterminer la tranche d'âge
                                        if age < 20:
                                            tranche = '<20'
                                        elif age < 25:
                                            tranche = '20-24'
                                        elif age < 30:
                                            tranche = '25-29'
                                        elif age < 35:
                                            tranche = '30-34'
                                        elif age < 40:
                                            tranche = '35-39'
                                        elif age < 45:
                                            tranche = '40-44'
                                        elif age < 50:
                                            tranche = '45-49'
                                        elif age < 55:
                                            tranche = '50-54'
                                        elif age < 60:
                                            tranche = '55-59'
                                        elif age < 65:
                                            tranche = '60-64'
                                        else:
                                            tranche = '65+'

                                        # Déterminer le sexe à partir du NIR
                                        if nir and len(nir) > 0:
                                            if nir[0] == '1':
                                                pyramide_hommes[tranche] += 1
                                            elif nir[0] == '2':
                                                pyramide_femmes[tranche] += 1
                                    except (ValueError, IndexError):
                                        pass

                        evolution_data['pyramide'] = {
                            'tranches': tranches,
                            'hommes': [pyramide_hommes[t] for t in tranches],
                            'femmes': [pyramide_femmes[t] for t in tranches],
                            'date_reference': date_reference_str
                        }

                        # Calculer l'âge moyen et l'ajouter aux stats
                        if ages_list and evolution_data.get('stats'):
                            evolution_data['stats']['age_moyen'] = int(round(sum(ages_list) / len(ages_list)))

                upload_success = True
            except Exception as e:
                import traceback
                traceback.print_exc()
                upload_error = f"Erreur lors de l'analyse des fichiers : {str(e)}"

    return render_template('evolution_effectif.html',
                         upload_success=upload_success,
                         upload_error=upload_error,
                         files_info=files_info,
                         evolution=evolution_data)

if __name__ == '__main__':
    import os
    import sys

    # Configuration UTF-8 pour Windows
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    port = int(os.environ.get('PORT', 8050))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'

    print("=" * 60)
    print("🚀 Application DSN Flask démarrée")
    print(f"📍 URL: http://localhost:{port}")
    print(f"🔧 Mode: {'Development' if debug else 'Production'}")
    print("=" * 60)

    app.run(debug=debug, host='0.0.0.0', port=port)
