-- Script pour identifier votre compte admin
-- Exécutez cette requête pour voir TOUS vos comptes

-- ============================================================
-- VOIR TOUS LES COMPTES AVEC LEUR RÔLE
-- ============================================================
SELECT 
    email,
    username,
    role,
    first_name,
    last_name,
    created_at
FROM users 
ORDER BY created_at DESC;

-- ============================================================
-- VOIR UNIQUEMENT LES COMPTES ADMIN
-- ============================================================
SELECT 
    email,
    username,
    role,
    first_name,
    last_name
FROM users 
WHERE role IN ('director', 'admin')
ORDER BY created_at DESC;

-- ============================================================
-- COMPTER LES COMPTES PAR RÔLE
-- ============================================================
SELECT 
    role,
    COUNT(*) as nombre
FROM users 
GROUP BY role;

-- ============================================================
-- VOIR LE COMPTE LE PLUS RÉCENT (probablement le vôtre)
-- ============================================================
SELECT 
    email,
    username,
    role,
    first_name,
    last_name,
    created_at
FROM users 
ORDER BY created_at DESC
LIMIT 1;



