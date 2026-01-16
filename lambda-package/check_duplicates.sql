-- Script SQL pour vérifier les doublons d'utilisateurs
-- À exécuter dans la base de données PostgreSQL

-- 1. Trouver les doublons par email (avant email_canonical)
SELECT email, COUNT(*) as count 
FROM users 
GROUP BY email 
HAVING COUNT(*) > 1
ORDER BY count DESC;

-- 2. Trouver les doublons par email_canonical (après migration)
SELECT email_canonical, COUNT(*) as count 
FROM users 
WHERE email_canonical IS NOT NULL
GROUP BY email_canonical 
HAVING COUNT(*) > 1
ORDER BY count DESC;

-- 3. Trouver les utilisateurs avec le même google_sub
SELECT google_sub, COUNT(*) as count 
FROM users 
WHERE google_sub IS NOT NULL 
GROUP BY google_sub 
HAVING COUNT(*) > 1
ORDER BY count DESC;

-- 4. Trouver le propriétaire d'un username spécifique
SELECT id, email, email_canonical, google_sub, username, created_at
FROM users 
WHERE LOWER(username) = LOWER('Laetibibi');

-- 5. Trouver tous les utilisateurs avec un email similaire (pour détecter les variantes)
-- Exemple: laetitia.imboden132@gmail.com vs laetitiaimboden132@gmail.com
SELECT 
    LOWER(REGEXP_REPLACE(SPLIT_PART(email, '@', 1), '\.', '', 'g')) || '@' || SPLIT_PART(email, '@', 2) as normalized_email,
    COUNT(*) as count,
    STRING_AGG(id::text, ', ') as user_ids,
    STRING_AGG(email, ', ') as emails
FROM users
WHERE email LIKE '%@gmail.com' OR email LIKE '%@googlemail.com'
GROUP BY normalized_email
HAVING COUNT(*) > 1
ORDER BY count DESC;

-- 6. Afficher tous les détails des utilisateurs avec un email donné (pour debug)
SELECT id, email, email_canonical, google_sub, username, first_name, last_name, created_at, password_hash IS NOT NULL as has_password
FROM users 
WHERE email LIKE '%laetitia%imboden%'
ORDER BY created_at DESC;

