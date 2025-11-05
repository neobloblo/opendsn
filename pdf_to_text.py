"""
Script pour convertir le PDF du cahier technique DSN en fichier texte
"""
import PyPDF2
import sys

def pdf_to_text(pdf_path, output_path):
    """Convertit un PDF en fichier texte"""
    print(f"Ouverture du fichier {pdf_path}...")

    try:
        with open(pdf_path, 'rb') as pdf_file:
            # Créer un lecteur PDF
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            total_pages = len(pdf_reader.pages)
            print(f"Nombre de pages : {total_pages}")

            # Extraire le texte de toutes les pages
            text = ""
            for i, page in enumerate(pdf_reader.pages, 1):
                print(f"Extraction page {i}/{total_pages}...", end='\r')
                text += f"\n\n{'='*80}\n"
                text += f"PAGE {i}\n"
                text += f"{'='*80}\n\n"
                text += page.extract_text()

            print(f"\nÉcriture dans {output_path}...")

            # Écrire dans le fichier texte
            with open(output_path, 'w', encoding='utf-8') as text_file:
                text_file.write(text)

            print(f"✅ Conversion terminée !")
            print(f"Fichier créé : {output_path}")
            print(f"Taille : {len(text)} caractères")

    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)

if __name__ == "__main__":
    pdf_path = "cahier_technique/dsn-cahier-technique-2025.1.pdf"
    output_path = "cahier_technique/dsn-cahier-technique-2025.1.txt"

    pdf_to_text(pdf_path, output_path)
