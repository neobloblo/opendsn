"""
Script pour extraire les rubriques DSN (S10, S20, S21, etc.) du cahier technique
et les insérer dans la base de données
"""
import re
import sqlite3
import sys

def extract_rubriques(text_file, structure_codes):
    """Extrait les rubriques pour les structures données"""

    with open(text_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    all_rubriques = []

    for structure_code in structure_codes:
        rubriques = []
        seen = set()

        # Pattern 1: Format avec type et taille (S20.G00.01.005  Code postal  C 5 5)
        pattern1 = rf'^({structure_code}\.G\d{{2}}\.\d{{2}}\.\d{{3}})\s+(.+?)\s+([CNDA])\s+(\d+)\s+(\d+)'

        # Pattern 2: Format avec O/C/I/N (S20.G00.00.001 Nom du logiciel utilisé O O O O O O)
        # Le nom s'arrête avant les lettres O/C/I/N isolées (indicateurs de contraintes)
        pattern2 = rf'^({structure_code}\.G\d{{2}}\.\d{{2}}\.\d{{3}})\s+(.+?)\s+[OCIN]\s+[OCIN]'

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
                    'structure_code': structure_code
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
                    'taille_max': 255,
                    'structure_code': structure_code
                })

        print(f"   ✅ {structure_code}: {len(rubriques)} rubriques trouvées")
        all_rubriques.extend(rubriques)

    return all_rubriques

def insert_rubriques_to_db(rubriques, structure_codes):
    """Insère les rubriques dans la base de données"""

    conn = sqlite3.connect('dsn.db')
    cursor = conn.cursor()

    # Supprimer les anciennes rubriques pour ces structures
    for structure_code in structure_codes:
        cursor.execute("DELETE FROM rubriques WHERE structure_code = ?", (structure_code,))

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
            pass

    conn.commit()
    conn.close()

    return inserted

if __name__ == "__main__":
    structures = ['S20', 'S21']

    print("=" * 60)
    print(f"Extraction des rubriques {', '.join(structures)}")
    print("=" * 60)

    # Extraire les rubriques
    print("\n1. Extraction depuis le fichier texte...")
    rubriques = extract_rubriques('cahier_technique/dsn-cahier-technique-2025.1.txt', structures)
    print(f"\n   Total : {len(rubriques)} rubriques trouvées")

    # Insérer dans la base
    print("\n2. Insertion dans la base de données...")
    inserted = insert_rubriques_to_db(rubriques, structures)
    print(f"   ✅ {inserted} rubriques insérées")

    print("\n" + "=" * 60)
    print("✅ Traitement terminé !")
    print("=" * 60)
