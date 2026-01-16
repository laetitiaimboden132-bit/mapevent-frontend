-- ============================================
-- Schéma de base de données pour MapEventAI
-- ============================================

-- Table des événements
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    date DATE,
    time TIME,
    categories JSONB DEFAULT '[]'::jsonb,
    likes_count INTEGER DEFAULT 0,
    favorites_count INTEGER DEFAULT 0,
    participations_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des bookings (hébergements)
CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    categories JSONB DEFAULT '[]'::jsonb,
    likes_count INTEGER DEFAULT 0,
    favorites_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des services
CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    categories JSONB DEFAULT '[]'::jsonb,
    likes_count INTEGER DEFAULT 0,
    favorites_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des utilisateurs (pour les actions)
-- Note: Pour l'instant, on utilise un système simple avec user_id comme string
-- Plus tard, on pourra créer une vraie table users avec authentification
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    username VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    subscription VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ajouter les colonnes si elles n'existent pas déjà (pour les bases existantes)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'first_name') THEN
        ALTER TABLE users ADD COLUMN first_name VARCHAR(100);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'last_name') THEN
        ALTER TABLE users ADD COLUMN last_name VARCHAR(100);
    END IF;
END $$;

-- Table des mots de passe utilisateur (séparée pour sécurité)
CREATE TABLE IF NOT EXISTS user_passwords (
    user_id VARCHAR(255) PRIMARY KEY,
    password_hash TEXT NOT NULL,
    salt VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_passwords_user ON user_passwords(user_id);

-- Table des likes (likes sur events, bookings, services)
CREATE TABLE IF NOT EXISTS user_likes (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    item_type VARCHAR(50) NOT NULL, -- 'event', 'booking', 'service'
    item_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, item_type, item_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_user_likes_user ON user_likes(user_id);
CREATE INDEX IF NOT EXISTS idx_user_likes_item ON user_likes(item_type, item_id);

-- Table des favoris
CREATE TABLE IF NOT EXISTS user_favorites (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    item_type VARCHAR(50) NOT NULL, -- 'event', 'booking', 'service'
    item_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, item_type, item_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_user_favorites_user ON user_favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_user_favorites_item ON user_favorites(item_type, item_id);

-- Table des participations (inscriptions aux événements)
CREATE TABLE IF NOT EXISTS user_participations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    item_type VARCHAR(50) NOT NULL, -- 'event' principalement
    item_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, item_type, item_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_user_participations_user ON user_participations(user_id);
CREATE INDEX IF NOT EXISTS idx_user_participations_item ON user_participations(item_type, item_id);

-- Table de l'agenda (événements ajoutés à l'agenda)
CREATE TABLE IF NOT EXISTS user_agenda (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    item_type VARCHAR(50) NOT NULL, -- 'event', 'booking', 'service'
    item_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, item_type, item_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_user_agenda_user ON user_agenda(user_id);
CREATE INDEX IF NOT EXISTS idx_user_agenda_item ON user_agenda(item_type, item_id);

-- Table des avis/commentaires (pour plus tard)
CREATE TABLE IF NOT EXISTS user_reviews (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    item_type VARCHAR(50) NOT NULL, -- 'event', 'booking', 'service'
    item_id INTEGER NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_user_reviews_item ON user_reviews(item_type, item_id);

-- Table des amis
CREATE TABLE IF NOT EXISTS user_friends (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    friend_id VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'accepted', 'blocked'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, friend_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (friend_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_friends_user ON user_friends(user_id);
CREATE INDEX IF NOT EXISTS idx_user_friends_friend ON user_friends(friend_id);
CREATE INDEX IF NOT EXISTS idx_user_friends_status ON user_friends(status);

-- Table des groupes
CREATE TABLE IF NOT EXISTS groups (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(20) DEFAULT 'public', -- 'public', 'private'
    category VARCHAR(100), -- Pour les canaux MapEvent automatiques
    country VARCHAR(10), -- Pour les canaux par pays
    creator_id VARCHAR(255) NOT NULL,
    icon VARCHAR(10) DEFAULT '👥',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_groups_creator ON groups(creator_id);
CREATE INDEX IF NOT EXISTS idx_groups_category ON groups(category);
CREATE INDEX IF NOT EXISTS idx_groups_country ON groups(country);

-- Table des membres de groupes
CREATE TABLE IF NOT EXISTS group_members (
    id SERIAL PRIMARY KEY,
    group_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'member', -- 'admin', 'moderator', 'member'
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_group_members_group ON group_members(group_id);
CREATE INDEX IF NOT EXISTS idx_group_members_user ON group_members(user_id);

-- Table des messages de groupes
CREATE TABLE IF NOT EXISTS group_messages (
    id SERIAL PRIMARY KEY,
    group_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    attachments JSONB DEFAULT '[]'::jsonb,
    status VARCHAR(20) DEFAULT 'published', -- 'published', 'pending_moderation', 'deleted'
    reactions JSONB DEFAULT '{}'::jsonb, -- {emoji: [user_ids]}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_group_messages_group ON group_messages(group_id);
CREATE INDEX IF NOT EXISTS idx_group_messages_user ON group_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_group_messages_status ON group_messages(status);
CREATE INDEX IF NOT EXISTS idx_group_messages_created ON group_messages(created_at DESC);

-- Table des signalements
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    reporter_id VARCHAR(255) NOT NULL,
    target_type VARCHAR(50) NOT NULL, -- 'user', 'message', 'group', 'event', 'booking', 'service'
    target_id VARCHAR(255) NOT NULL,
    reason VARCHAR(100),
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'reviewed', 'resolved', 'dismissed'
    reviewed_by VARCHAR(255),
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reporter_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_reports_reporter ON reports(reporter_id);
CREATE INDEX IF NOT EXISTS idx_reports_target ON reports(target_type, target_id);
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);

-- Table des profils utilisateurs
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id VARCHAR(255) PRIMARY KEY,
    bio TEXT,
    profile_photos JSONB DEFAULT '[]'::jsonb,
    profile_videos JSONB DEFAULT '[]'::jsonb,
    profile_links JSONB DEFAULT '[]'::jsonb,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table des alertes sociales
CREATE TABLE IF NOT EXISTS social_alerts (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'friend_request', 'event_invitation', 'group_mention', etc.
    from_user_id VARCHAR(255),
    title VARCHAR(255),
    message TEXT,
    icon VARCHAR(10),
    metadata JSONB DEFAULT '{}'::jsonb, -- Données supplémentaires (eventId, groupId, etc.)
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (from_user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_social_alerts_user ON social_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_social_alerts_read ON social_alerts(user_id, read);
CREATE INDEX IF NOT EXISTS idx_social_alerts_created ON social_alerts(created_at DESC);

-- Table de modération d'images
CREATE TABLE IF NOT EXISTS image_moderation (
    id SERIAL PRIMARY KEY,
    image_url TEXT NOT NULL,
    user_id VARCHAR(255),
    moderation_result JSONB, -- Résultat de l'API de modération
    is_safe BOOLEAN DEFAULT TRUE,
    moderation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_image_moderation_url ON image_moderation(image_url);
CREATE INDEX IF NOT EXISTS idx_image_moderation_user ON image_moderation(user_id);

-- Table des signalements
CREATE TABLE IF NOT EXISTS user_reports (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    item_type VARCHAR(50) NOT NULL, -- 'event', 'booking', 'service', 'message', 'discussion', 'review', 'user', etc.
    item_id VARCHAR(255) NOT NULL, -- Peut être INTEGER ou VARCHAR selon le type
    parent_type VARCHAR(50), -- Type parent si c'est un message dans une discussion
    parent_id VARCHAR(255), -- ID parent si c'est un message dans une discussion
    reason VARCHAR(100) NOT NULL, -- 'inappropriate', 'fake', 'offensive', 'spam', 'other'
    details TEXT, -- Détails supplémentaires
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'reviewed', 'resolved', 'dismissed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_user_reports_user ON user_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_user_reports_item ON user_reports(item_type, item_id);
CREATE INDEX IF NOT EXISTS idx_user_reports_status ON user_reports(status);

-- Table des discussions/messages (pour plus tard)
CREATE TABLE IF NOT EXISTS discussions (
    id SERIAL PRIMARY KEY,
    item_type VARCHAR(50) NOT NULL, -- 'event', 'booking', 'service'
    item_id INTEGER NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_discussions_item ON discussions(item_type, item_id);

-- Fonction pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers pour mettre à jour updated_at
DROP TRIGGER IF EXISTS update_events_updated_at ON events;
CREATE TRIGGER update_events_updated_at BEFORE UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_bookings_updated_at ON bookings;
CREATE TRIGGER update_bookings_updated_at BEFORE UPDATE ON bookings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_services_updated_at ON services;
CREATE TRIGGER update_services_updated_at BEFORE UPDATE ON services
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_reviews_updated_at ON user_reviews;
CREATE TRIGGER update_user_reviews_updated_at BEFORE UPDATE ON user_reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Fonctions pour mettre à jour les compteurs (likes, favorites, participations)
CREATE OR REPLACE FUNCTION update_likes_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.item_type = 'event' THEN
            UPDATE events SET likes_count = likes_count + 1 WHERE id = NEW.item_id;
        ELSIF NEW.item_type = 'booking' THEN
            UPDATE bookings SET likes_count = likes_count + 1 WHERE id = NEW.item_id;
        ELSIF NEW.item_type = 'service' THEN
            UPDATE services SET likes_count = likes_count + 1 WHERE id = NEW.item_id;
        END IF;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        IF OLD.item_type = 'event' THEN
            UPDATE events SET likes_count = GREATEST(likes_count - 1, 0) WHERE id = OLD.item_id;
        ELSIF OLD.item_type = 'booking' THEN
            UPDATE bookings SET likes_count = GREATEST(likes_count - 1, 0) WHERE id = OLD.item_id;
        ELSIF OLD.item_type = 'service' THEN
            UPDATE services SET likes_count = GREATEST(likes_count - 1, 0) WHERE id = OLD.item_id;
        END IF;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS trigger_update_likes_count ON user_likes;
CREATE TRIGGER trigger_update_likes_count
    AFTER INSERT OR DELETE ON user_likes
    FOR EACH ROW EXECUTE FUNCTION update_likes_count();

CREATE OR REPLACE FUNCTION update_favorites_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.item_type = 'event' THEN
            UPDATE events SET favorites_count = favorites_count + 1 WHERE id = NEW.item_id;
        ELSIF NEW.item_type = 'booking' THEN
            UPDATE bookings SET favorites_count = favorites_count + 1 WHERE id = NEW.item_id;
        ELSIF NEW.item_type = 'service' THEN
            UPDATE services SET favorites_count = favorites_count + 1 WHERE id = NEW.item_id;
        END IF;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        IF OLD.item_type = 'event' THEN
            UPDATE events SET favorites_count = GREATEST(favorites_count - 1, 0) WHERE id = OLD.item_id;
        ELSIF OLD.item_type = 'booking' THEN
            UPDATE bookings SET favorites_count = GREATEST(favorites_count - 1, 0) WHERE id = OLD.item_id;
        ELSIF OLD.item_type = 'service' THEN
            UPDATE services SET favorites_count = GREATEST(favorites_count - 1, 0) WHERE id = OLD.item_id;
        END IF;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS trigger_update_favorites_count ON user_favorites;
CREATE TRIGGER trigger_update_favorites_count
    AFTER INSERT OR DELETE ON user_favorites
    FOR EACH ROW EXECUTE FUNCTION update_favorites_count();

CREATE OR REPLACE FUNCTION update_participations_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.item_type = 'event' THEN
            UPDATE events SET participations_count = participations_count + 1 WHERE id = NEW.item_id;
        END IF;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        IF OLD.item_type = 'event' THEN
            UPDATE events SET participations_count = GREATEST(participations_count - 1, 0) WHERE id = OLD.item_id;
        END IF;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS trigger_update_participations_count ON user_participations;
CREATE TRIGGER trigger_update_participations_count
    AFTER INSERT OR DELETE ON user_participations
    FOR EACH ROW EXECUTE FUNCTION update_participations_count();

-- Table des paiements
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    stripe_customer_id VARCHAR(255),
    stripe_session_id VARCHAR(255) UNIQUE,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CHF',
    status VARCHAR(50) NOT NULL, -- pending, succeeded, failed, refunded
    payment_type VARCHAR(50) NOT NULL, -- contact, subscription, donation, cart
    item_type VARCHAR(50), -- booking, service, subscription_plan
    item_id INTEGER,
    items JSONB, -- Pour les paniers (array d'items)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_stripe_payment_intent_id ON payments(stripe_payment_intent_id);
CREATE INDEX IF NOT EXISTS idx_payments_stripe_session_id ON payments(stripe_session_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);

-- Table des abonnements
CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    stripe_subscription_id VARCHAR(255) UNIQUE NOT NULL,
    stripe_customer_id VARCHAR(255),
    plan VARCHAR(50) NOT NULL, -- events-explorer, events-alerts-pro, service-pro, service-ultra, full-premium
    status VARCHAR(50) NOT NULL, -- active, canceled, past_due, trialing, incomplete
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_subscription_id ON subscriptions(stripe_subscription_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);

-- Trigger pour mettre à jour updated_at sur payments
DROP TRIGGER IF EXISTS update_payments_updated_at ON payments;
CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger pour mettre à jour updated_at sur subscriptions
DROP TRIGGER IF EXISTS update_subscriptions_updated_at ON subscriptions;
CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Table des alertes utilisateur
CREATE TABLE IF NOT EXISTS user_alerts (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    event_id INTEGER NOT NULL,
    favorite_id VARCHAR(255) NOT NULL,
    favorite_name VARCHAR(255) NOT NULL,
    favorite_mode VARCHAR(50) NOT NULL, -- 'event', 'booking', 'service', 'avatar'
    distance DECIMAL(10, 2), -- Distance entre favori et événement
    distance_to_user DECIMAL(10, 2), -- Distance entre utilisateur et événement
    closest_address VARCHAR(255), -- Adresse la plus proche
    status VARCHAR(50) DEFAULT 'new', -- 'new', 'seen', 'deleted'
    is_blurred BOOLEAN DEFAULT FALSE,
    event_title VARCHAR(255),
    event_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    seen_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_user_alerts_user ON user_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_user_alerts_event ON user_alerts(event_id);
CREATE INDEX IF NOT EXISTS idx_user_alerts_status ON user_alerts(user_id, status);


