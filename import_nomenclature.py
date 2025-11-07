#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour importer la nomenclature PCS-ESE dans la base de données
"""
import sqlite3
import os

def import_nomenclature():
    """Importe la nomenclature PCS-ESE dans la base de données"""
    # Chemins
    db_path = os.path.join(os.path.dirname(__file__), 'dsn.db')
    sql_path = os.path.join(os.path.dirname(__file__), 'nomenclature_pcs_ese.sql')

    print(f"Connexion à la base de données : {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("Suppression de la table existante si presente...")
        cursor.execute("DROP TABLE IF EXISTS nomenclature_pcs_ese")
        conn.commit()

        print(f"Lecture du fichier SQL : {sql_path}")
        with open(sql_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        print("Execution du script SQL...")
        cursor.executescript(sql_script)
        conn.commit()

        # Vérifier le nombre de lignes importées
        cursor.execute("SELECT COUNT(*) FROM nomenclature_pcs_ese")
        count = cursor.fetchone()[0]
        print(f"OK - {count} codes PCS-ESE importes avec succes !")

        # Afficher quelques exemples
        print("\nQuelques exemples de codes importes :")
        cursor.execute("SELECT code, libelle FROM nomenclature_pcs_ese ORDER BY code LIMIT 10")
        for row in cursor.fetchall():
            print(f"  {row[0]:8s} : {row[1]}")

    except Exception as e:
        print(f"ERREUR lors de l'import : {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    import_nomenclature()
