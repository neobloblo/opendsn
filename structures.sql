-- Table des structures hiérarchiques DSN
CREATE TABLE IF NOT EXISTS structures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(10) NOT NULL UNIQUE,  -- S10, S20, S21, etc.
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    ordre INTEGER,
    actif BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertion des structures principales
INSERT INTO structures (code, nom, description, ordre) VALUES
('S10', 'Entête', 'Informations sur l''émetteur et l''envoi du fichier DSN', 1),
('S20', 'Déclaration', 'Informations sur la déclaration', 2),
('S21', 'Individu', 'Données relatives aux individus/salariés', 3),
('S40', 'Entreprise', 'Informations sur l''entreprise', 4);
