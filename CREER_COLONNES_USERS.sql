-- Script SQL pour créer toutes les colonnes nécessaires dans la table users
-- À exécuter une seule fois sur votre base de données PostgreSQL

-- Colonnes de base
ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(255);

-- Colonnes OAuth
ALTER TABLE users ADD COLUMN IF NOT EXISTS oauth_google_id VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS oauth_facebook_id VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS oauth_apple_id VARCHAR(255);

-- Colonnes de sécurité
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

-- Colonnes d'avatar (TEXT pour supporter les URLs longues)
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_emoji TEXT DEFAULT '';
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_description TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_photo_url TEXT;

-- Colonnes d'adresse
ALTER TABLE users ADD COLUMN IF NOT EXISTS postal_address TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS postal_city TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS postal_zip TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS postal_country VARCHAR(10) DEFAULT 'CH';

-- Colonnes de rôle et abonnement
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'user';
ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription VARCHAR(50) DEFAULT 'free';

-- Colonnes de dates
ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Modifier avatar_emoji si elle existe déjà avec VARCHAR(10)
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' 
        AND column_name = 'avatar_emoji' 
        AND character_maximum_length = 10
    ) THEN
        ALTER TABLE users ALTER COLUMN avatar_emoji TYPE TEXT;
    END IF;
END $$;

-- Créer des index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_users_email ON users(LOWER(email));
CREATE INDEX IF NOT EXISTS idx_users_oauth_google_id ON users(oauth_google_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(LOWER(username));

COMMENT ON TABLE users IS 'Table des utilisateurs MapEvent avec support OAuth complet';









