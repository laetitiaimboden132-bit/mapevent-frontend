-- Migration: Ajouter les champs d'adresse dans la table users
-- Date: 2026-01-07

-- Ajouter les colonnes d'adresse si elles n'existent pas
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS address_label VARCHAR(500),
ADD COLUMN IF NOT EXISTS address_lat DECIMAL(10, 8),
ADD COLUMN IF NOT EXISTS address_lng DECIMAL(11, 8),
ADD COLUMN IF NOT EXISTS address_country_code VARCHAR(2),
ADD COLUMN IF NOT EXISTS address_city VARCHAR(100),
ADD COLUMN IF NOT EXISTS address_postcode VARCHAR(20),
ADD COLUMN IF NOT EXISTS address_street VARCHAR(200);

-- Créer un index sur les coordonnées pour les recherches de proximité
CREATE INDEX IF NOT EXISTS idx_users_address_coords ON users(address_lat, address_lng) WHERE address_lat IS NOT NULL AND address_lng IS NOT NULL;

-- Créer la table user_alert_settings pour les paramètres d'alertes
CREATE TABLE IF NOT EXISTS user_alert_settings (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    alert_radius_km INTEGER DEFAULT 50, -- Rayon en km pour les alertes de proximité
    categories TEXT[], -- Catégories d'événements à surveiller
    frequency VARCHAR(20) DEFAULT 'realtime', -- realtime, daily, weekly
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Créer un index sur user_id pour les recherches rapides
CREATE INDEX IF NOT EXISTS idx_user_alert_settings_user_id ON user_alert_settings(user_id);

COMMENT ON TABLE user_alert_settings IS 'Paramètres d''alertes personnalisées pour chaque utilisateur';
COMMENT ON COLUMN user_alert_settings.alert_radius_km IS 'Rayon en kilomètres pour les alertes de proximité';
COMMENT ON COLUMN user_alert_settings.categories IS 'Tableau de catégories d''événements à surveiller';
COMMENT ON COLUMN user_alert_settings.frequency IS 'Fréquence des alertes: realtime, daily, weekly';



