"""
Script pour extraire les sous-groupes DSN (S10.G00.01, S21.G00.06, etc.) du cahier technique
et les insérer dans la base de données
"""
import re
import sqlite3

def extract_sous_groupes(text_file, structure_codes):
    """Extrait les sous-groupes pour les structures données"""

    with open(text_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    all_sous_groupes = []

    for structure_code in structure_codes:
        sous_groupes = []
        seen = set()

        # Pattern pour les sous-groupes: S10.G00.01 - Emetteur (1,1)
        # Format strict: code - nom(cardinalité) ou code - nom (cardinalité)
        # La cardinalité doit être du type: 0,1 ou 0,* ou 1,1 ou 1,*
        pattern = rf'^({structure_code}\.G\d{{2}}\.\d{{2}})\s*[-–]\s*(.+?)\s*\(([0-9]+,[0-9*]+)\)\s*$'

        for line in lines:
            line = line.strip()

            match = re.match(pattern, line)
            if match:
                code = match.group(1)

                if code in seen:
                    continue
                seen.add(code)

                nom = match.group(2).strip()
                cardinalite = match.group(3).strip()

                sous_groupes.append({
                    'code': code,
                    'structure_code': structure_code,
                    'nom': nom,
                    'cardinalite': cardinalite
                })

        print(f"   ✅ {structure_code}: {len(sous_groupes)} sous-groupes trouvés")

        # Afficher quelques exemples pour vérification
        if sous_groupes:
            print(f"      Exemples:")
            for sg in sous_groupes[:3]:
                print(f"      - {sg['code']}: {sg['nom']} {sg['cardinalite']}")

        all_sous_groupes.extend(sous_groupes)

    return all_sous_groupes

def insert_sous_groupes_to_db(sous_groupes, structure_codes):
    """Insère les sous-groupes dans la base de données"""

    conn = sqlite3.connect('dsn.db')
    cursor = conn.cursor()

    # Supprimer les anciens sous-groupes pour ces structures
    for structure_code in structure_codes:
        cursor.execute("DELETE FROM sous_groupes WHERE structure_code = ?", (structure_code,))

    # Insérer les nouveaux sous-groupes
    inserted = 0
    for i, sg in enumerate(sous_groupes, 1):
        try:
            cursor.execute("""
                INSERT INTO sous_groupes (code, structure_code, nom, cardinalite, ordre)
                VALUES (?, ?, ?, ?, ?)
            """, (
                sg['code'],
                sg['structure_code'],
                sg['nom'],
                sg['cardinalite'],
                i
            ))
            inserted += 1
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()

    return inserted

def link_rubriques_to_sous_groupes():
    """Lie les rubriques existantes à leurs sous-groupes"""

    conn = sqlite3.connect('dsn.db')
    cursor = conn.cursor()

    # Récupérer toutes les rubriques
    cursor.execute("SELECT code FROM rubriques")
    rubriques = cursor.fetchall()

    updated = 0
    for (rubrique_code,) in rubriques:
        # Extraire le code du sous-groupe depuis le code de la rubrique
        # Ex: S10.G00.01.005 -> S10.G00.01
        parts = rubrique_code.split('.')
        if len(parts) == 4:  # Format: S10.G00.01.005 (4 parties)
            sous_groupe_code = '.'.join(parts[:3])  # Prendre S10.G00.01 (3 premières parties)

            # Vérifier si le sous-groupe existe
            cursor.execute("SELECT id FROM sous_groupes WHERE code = ?", (sous_groupe_code,))
            if cursor.fetchone():
                cursor.execute(
                    "UPDATE rubriques SET sous_groupe_code = ? WHERE code = ?",
                    (sous_groupe_code, rubrique_code)
                )
                updated += 1

    conn.commit()
    conn.close()

    return updated

if __name__ == "__main__":
    structures = ['S10', 'S20', 'S21']

    print("=" * 60)
    print(f"Extraction des sous-groupes {', '.join(structures)}")
    print("=" * 60)

    # Extraire les sous-groupes
    print("\n1. Extraction depuis le fichier texte...")
    sous_groupes = extract_sous_groupes('cahier_technique/dsn-cahier-technique-2025.1.txt', structures)
    print(f"\n   Total : {len(sous_groupes)} sous-groupes trouvés")

    # Insérer dans la base
    print("\n2. Insertion dans la base de données...")
    inserted = insert_sous_groupes_to_db(sous_groupes, structures)
    print(f"   ✅ {inserted} sous-groupes insérés")

    # Lier les rubriques aux sous-groupes
    print("\n3. Liaison des rubriques aux sous-groupes...")
    updated = link_rubriques_to_sous_groupes()
    print(f"   ✅ {updated} rubriques liées à leurs sous-groupes")

    print("\n" + "=" * 60)
    print("✅ Traitement terminé !")
    print("=" * 60)
