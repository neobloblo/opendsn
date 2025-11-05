"""
Application Flask DSN - Gestion de la norme DSN
"""
from flask import Flask, render_template, request
import sqlite3
import pandas as pd

app = Flask(__name__)

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

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8050))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'

    print("=" * 60)
    print("🚀 Application DSN Flask démarrée")
    print(f"📍 URL: http://localhost:{port}")
    print(f"🔧 Mode: {'Development' if debug else 'Production'}")
    print("=" * 60)

    app.run(debug=debug, host='0.0.0.0', port=port)
