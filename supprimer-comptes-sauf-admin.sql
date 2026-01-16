-- ============================================================
-- SCRIPT SQL POUR GARDER UNIQUEMENT LE COMPTE ADMIN
-- ============================================================
-- INSTRUCTIONS:
-- 1. Allez sur AWS Console > RDS > mapevent-db
-- 2. Cliquez sur "Query Editor" ou "Éditeur de requêtes"
-- 3. Connectez-vous avec vos identifiants RDS
-- 4. Copiez-collez ce script
-- 5. REMPLACEZ 'admin@example.com' par l'email de votre compte admin
-- 6. Exécutez le script
-- ============================================================

BEGIN;

-- Afficher tous les comptes avant suppression
SELECT 
    u.id,
    u.email,
    u.username,
    COALESCE(u.role, 'user') as role,
    u.created_at,
    CASE 
        WHEN COALESCE(u.role, 'user') IN ('admin', 'director') THEN 'ADMIN/DIRECTOR'
        ELSE 'USER'
    END as role_type
FROM users u
ORDER BY u.created_at DESC;

-- Supprimer tous les comptes SAUF le compte admin
-- ⚠️ REMPLACEZ 'admin@example.com' par l'email de votre compte admin ! ⚠️
DELETE FROM user_favorites
WHERE user_id NOT IN (
    SELECT id FROM users WHERE email = 'admin@example.com'
);

DELETE FROM user_agenda
WHERE user_id NOT IN (
    SELECT id FROM users WHERE email = 'admin@example.com'
);

DELETE FROM user_likes
WHERE user_id NOT IN (
    SELECT id FROM users WHERE email = 'admin@example.com'
);

DELETE FROM subscriptions
WHERE user_id NOT IN (
    SELECT id FROM users WHERE email = 'admin@example.com'
);

DELETE FROM user_passwords
WHERE user_id NOT IN (
    SELECT id FROM users WHERE email = 'admin@example.com'
);

DELETE FROM user_profiles
WHERE user_id NOT IN (
    SELECT id FROM users WHERE email = 'admin@example.com'
);

DELETE FROM users
WHERE email != 'admin@example.com';

-- Afficher le compte restant (doit être l'admin)
SELECT 
    u.id,
    u.email,
    u.username,
    u.first_name,
    u.last_name,
    COALESCE(u.role, 'user') as role,
    u.created_at
FROM users u;

COMMIT;

-- ============================================================
-- VÉRIFICATION
-- ============================================================
-- Si tout s'est bien passé, vous devriez voir UN SEUL compte
-- avec l'email que vous avez spécifié
-- ============================================================
