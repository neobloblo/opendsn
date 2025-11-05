"""
Script pour extraire les rubriques S10 du cahier technique DSN
et les insérer dans la base de données
"""
import re
import sqlite3

def extract_s10_rubriques(text_file):
    """Extrait les rubriques S10 du fichier texte"""

    with open(text_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    rubriques = []
    seen = set()  # Pour éviter les doublons

    # Pattern 1: Format avec type et taille (S10.G00.01.005  Code postal  C 5 5)
    pattern1 = r'^(S10\.G\d{2}\.\d{2}\.\d{3})\s+(.+?)\s+([CNDA])\s+(\d+)\s+(\d+)'

    # Pattern 2: Format avec O/C (S10.G00.00.001 Nom du logiciel utilisé O O O O O O)
    pattern2 = r'^(S10\.G\d{2}\.\d{2}\.\d{3})\s+(.+?)\s+[OC]\s+[OC]'

    for line in lines:
        line = line.strip()

        # Essayer le pattern 1 (avec type et taille)
        match1 = re.match(pattern1, line)
        if match1:
            code = match1.group(1)

            if code in seen:
                continue
            seen.add(code)

            nom = match1.group(2).strip()
            type_donnee = match1.group(3)
            taille_max = int(match1.group(5))

            type_map = {'C': 'Texte', 'N': 'Numérique', 'D': 'Date', 'A': 'Alphanumérique'}
            type_donnee_fr = type_map.get(type_donnee, type_donnee)

            rubriques.append({
                'code': code,
                'nom': nom,
                'type_donnee': type_donnee_fr,
                'taille_max': taille_max,
                'structure_code': 'S10'
            })
            continue

        # Essayer le pattern 2 (avec O/C)
        match2 = re.match(pattern2, line)
        if match2:
            code = match2.group(1)

            if code in seen:
                continue
            seen.add(code)

            nom = match2.group(2).strip()

            rubriques.append({
                'code': code,
                'nom': nom,
                'type_donnee': 'Texte',
                'taille_max': 255,  # Valeur par défaut
                'structure_code': 'S10'
            })

    return rubriques

def insert_rubriques_to_db(rubriques):
    """Insère les rubriques dans la base de données"""

    conn = sqlite3.connect('dsn.db')
    cursor = conn.cursor()

    # Supprimer les anciennes rubriques S10 (sauf les exemples)
    cursor.execute("DELETE FROM rubriques WHERE structure_code = 'S10'")

    # Insérer les nouvelles rubriques
    inserted = 0
    for rubrique in rubriques:
        try:
            cursor.execute("""
                INSERT INTO rubriques (code, structure_code, nom, type_donnee, taille_max, obligatoire)
                VALUES (?, ?, ?, ?, ?, 0)
            """, (
                rubrique['code'],
                rubrique['structure_code'],
                rubrique['nom'],
                rubrique['type_donnee'],
                rubrique['taille_max']
            ))
            inserted += 1
        except sqlite3.IntegrityError:
            # Rubrique déjà existante
            pass

    conn.commit()
    conn.close()

    return inserted

if __name__ == "__main__":
    print("=" * 60)
    print("Extraction des rubriques S10")
    print("=" * 60)

    # Extraire les rubriques
    print("\n1. Extraction depuis le fichier texte...")
    rubriques = extract_s10_rubriques('cahier_technique/dsn-cahier-technique-2025.1.txt')
    print(f"   ✅ {len(rubriques)} rubriques S10 trouvées")

    # Afficher quelques exemples
    print("\n2. Exemples de rubriques extraites :")
    for rubrique in rubriques[:5]:
        print(f"   - {rubrique['code']}: {rubrique['nom']} ({rubrique['type_donnee']}, max {rubrique['taille_max']})")

    # Insérer dans la base
    print("\n3. Insertion dans la base de données...")
    inserted = insert_rubriques_to_db(rubriques)
    print(f"   ✅ {inserted} rubriques insérées")

    print("\n" + "=" * 60)
    print("✅ Traitement terminé !")
    print("=" * 60)
