-- Table des sous-groupes DSN (ex: S10.G00.01, S21.G00.06, etc.)
CREATE TABLE IF NOT EXISTS sous_groupes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) NOT NULL UNIQUE,  -- Ex: S10.G00.01
    structure_code VARCHAR(10) NOT NULL,  -- Ex: S10
    nom VARCHAR(200) NOT NULL,  -- Ex: Emetteur
    description TEXT,
    cardinalite VARCHAR(20),  -- Ex: (1,1) ou (0,N)
    ordre INTEGER,
    actif BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (structure_code) REFERENCES structures(code)
);

-- Index pour recherche rapide par structure
CREATE INDEX IF NOT EXISTS idx_sous_groupes_structure ON sous_groupes(structure_code);

-- Ajouter une colonne sous_groupe_code dans la table rubriques
ALTER TABLE rubriques ADD COLUMN sous_groupe_code VARCHAR(20);

-- Index pour lier les rubriques aux sous-groupes
CREATE INDEX IF NOT EXISTS idx_rubriques_sous_groupe ON rubriques(sous_groupe_code);
