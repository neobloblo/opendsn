"""
Page simple pour afficher les structures DSN
"""
import sqlite3

def afficher_structures():
    """Affiche les structures depuis la base de données"""
    conn = sqlite3.connect('dsn.db')
    cursor = conn.cursor()

    cursor.execute("SELECT code, nom, description, ordre FROM structures ORDER BY ordre")
    structures = cursor.fetchall()

    print("\n" + "="*70)
    print("STRUCTURES HIÉRARCHIQUES DSN")
    print("="*70 + "\n")

    for code, nom, description, ordre in structures:
        print(f"{ordre}. {code} - {nom}")
        print(f"   {description}")
        print()

    conn.close()

if __name__ == "__main__":
    afficher_structures()
