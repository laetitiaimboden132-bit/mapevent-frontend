-- Script SQL pour supprimer TOUS les comptes utilisateurs
-- ATTENTION: Cette opération est IRRÉVERSIBLE!

-- ============================================================
-- ÉTAPE 1: Vérifier combien de comptes existent
-- ============================================================
SELECT COUNT(*) as nombre_utilisateurs FROM users;

-- ============================================================
-- ÉTAPE 2: Voir la liste des utilisateurs (optionnel)
-- ============================================================
SELECT id, email, username, role, created_at FROM users ORDER BY created_at DESC;

-- ============================================================
-- ÉTAPE 3: SUPPRIMER TOUS LES COMPTES
-- ============================================================
-- ⚠️ ATTENTION: Cette commande supprimera TOUS les utilisateurs
-- Les données associées seront supprimées automatiquement via CASCADE:
-- - user_passwords
-- - user_likes
-- - user_favorites
-- - user_agenda
-- - user_participations
-- - user_reviews
-- - subscriptions
-- - etc.

-- DÉCOMMENTEZ LA LIGNE CI-DESSOUS POUR EXÉCUTER LA SUPPRESSION:
-- DELETE FROM users;

-- ============================================================
-- ÉTAPE 4: Vérifier que tout a été supprimé
-- ============================================================
-- SELECT COUNT(*) as nombre_utilisateurs_restants FROM users;
-- (Devrait retourner 0)



