-- Table des rubriques DSN
CREATE TABLE IF NOT EXISTS rubriques (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) NOT NULL UNIQUE,  -- Ex: S10.G00.00.001
    structure_code VARCHAR(10) NOT NULL,  -- Ex: S10
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    type_donnee VARCHAR(50),  -- Texte, Numérique, Date, etc.
    taille_max INTEGER,  -- Taille maximale du champ
    obligatoire BOOLEAN DEFAULT 0,
    format VARCHAR(100),  -- Format attendu (ex: NNNNNNNNNNNNNN pour SIRET)
    actif BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (structure_code) REFERENCES structures(code)
);

-- Index pour recherche rapide par structure
CREATE INDEX IF NOT EXISTS idx_rubriques_structure ON rubriques(structure_code);

-- Insertion de quelques rubriques S10 (Entête) comme exemples
INSERT INTO rubriques (code, structure_code, nom, description, type_donnee, taille_max, obligatoire, format) VALUES
('S10.G00.00.001', 'S10', 'SIRET', 'Numéro SIRET de l''émetteur', 'Numérique', 14, 1, 'NNNNNNNNNNNNNN'),
('S10.G00.00.002', 'S10', 'Raison sociale', 'Raison sociale de l''émetteur', 'Texte', 100, 1, NULL),
('S10.G00.00.003', 'S10', 'Type de déclarant', 'Type de déclarant (01=Employeur, 02=Tiers)', 'Numérique', 2, 1, 'NN'),
('S10.G00.00.004', 'S10', 'Date d''envoi', 'Date d''envoi de la déclaration', 'Date', 8, 1, 'AAAAMMJJ'),
('S10.G00.00.005', 'S10', 'Heure d''envoi', 'Heure d''envoi de la déclaration', 'Heure', 6, 0, 'HHMMSS'),
('S10.G00.00.006', 'S10', 'Version de la norme', 'Version de la norme DSN utilisée', 'Texte', 10, 1, NULL),
('S10.G00.00.007', 'S10', 'Logiciel émetteur', 'Nom du logiciel émetteur', 'Texte', 100, 0, NULL),
('S10.G00.00.008', 'S10', 'Version du logiciel', 'Version du logiciel émetteur', 'Texte', 50, 0, NULL);
