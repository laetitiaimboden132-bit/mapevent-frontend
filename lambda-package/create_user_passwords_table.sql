-- Script SQL pour créer la table user_passwords
-- À exécuter dans PostgreSQL (RDS)

-- Créer la table user_passwords si elle n'existe pas
CREATE TABLE IF NOT EXISTS user_passwords (
    user_id VARCHAR(255) PRIMARY KEY,
    password_hash TEXT NOT NULL,
    salt VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ajouter la contrainte de clé étrangère si la table users existe
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
        -- Vérifier si la contrainte existe déjà
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE constraint_name = 'user_passwords_user_id_fkey'
        ) THEN
            ALTER TABLE user_passwords 
            ADD CONSTRAINT user_passwords_user_id_fkey 
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
        END IF;
    END IF;
END $$;

-- Créer un index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_user_passwords_user ON user_passwords(user_id);

-- Vérifier que la table a été créée
SELECT 
    table_name, 
    column_name, 
    data_type 
FROM information_schema.columns 
WHERE table_name = 'user_passwords' 
ORDER BY ordinal_position;




