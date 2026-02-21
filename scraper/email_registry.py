# -*- coding: utf-8 -*-
"""
Registre centralisé des emails promo envoyés.
TOUJOURS utiliser ce module avant d'envoyer un email promo.

Usage:
    from email_registry import was_already_sent, mark_as_sent, filter_new_recipients

    # Vérifier un seul email
    if was_already_sent("info@example.com"):
        print("Déjà envoyé, on skip")

    # Filtrer une liste
    new_only = filter_new_recipients(["a@b.com", "c@d.com"])

    # Marquer comme envoyé après succès
    mark_as_sent("info@example.com", script="send_35_promo.py", context="Tourisme Zurich")

TECHNIQUE DE RECHERCHE SAFE (OBLIGATOIRE) :
============================================

ÉTAPE 1 - SÉLECTION DE L'EVENT :
  → Ouvrir all_events_dump.json (ou requête API /api/events)
  → Choisir un event RÉEL avec un event_id CONFIRMÉ sur la carte
  → Privilégier : festivals nommés, salons, concerts de salles indépendantes
  → Éviter : events opendata génériques (ateliers de centre civique, etc.)

ÉTAPE 2 - RECHERCHE DU TITRE SUR INTERNET :
  → Copier le TITRE EXACT de l'event
  → Rechercher : "{titre event} organisateur email contact"
  → Chercher : le site OFFICIEL de l'event (pas un agrégateur)
  → Trouver la page ÉQUIPE / TEAM / CONTACT / PRESSE du site officiel

ÉTAPE 3 - EXTRACTION DU CONTACT PERSONNEL :
  → Sur la page équipe, chercher des emails au format prenom@domaine.com
  → Exemples trouvés qui marchent :
    - tanguy.massines@lelieuunique.com (Le Lieu Unique, Nantes)
    - frederic@tipandshaft.com (Sailorz Film Festival)
    - annavictori@teatrepoliorama.com (Teatre Poliorama, Barcelona)
    - william@metropolisbleu.org (Festival Métropolis Bleu, Montréal)
    - marie-andree.lamontagne@metropolisbleu.org (Métropolis Bleu)
    - axelle@palpfestival.ch (PALP Festival, Valais)
  → Si la page équipe n'affiche PAS d'emails individuels → PASSER à l'event suivant
  → NE JAMAIS deviner/inventer un format d'email (prenom@domaine)

ÉTAPE 4 - VÉRIFICATION AVANT ENVOI :
  → L'email n'est PAS dans promo_emails_sent.json
  → Le domaine n'a PAS déjà 3 contacts (MAX_CONTACTS_PER_DOMAIN)
  → L'email passe is_blocked_email() → pas de prefixe/domaine bloqué
  → L'event_id existe VRAIMENT sur la carte
  → Les infos de l'event (date, lieu) sont CORRECTES et VÉRIFIÉES

RÈGLES ABSOLUES :
  → JAMAIS : info@, contact@, press@, admin@, billing@, reservation@, etc.
  → JAMAIS : concurrents (eventbrite, ticketmaster, ra.co, etc.)
  → JAMAIS : emails génériques de rôle (booking@, team@, communication@, etc.)
  → JAMAIS : inventer des dates/adresses - vérifier sur le site source
  → JAMAIS : envoyer 2x au même email OU à la même organisation
  → JAMAIS : deviner un email à partir du nom (chercher l'email PUBLIÉ)
  → Vérifier les DOUBLONS par domaine (max 3 contacts par organisation)

EMAILS MULTILINGUES (OBLIGATOIRE) :
====================================
  → L'email promo DOIT être dans la LANGUE OFFICIELLE du pays de l'event
  → Utiliser detect_lang(location) de send_35_promo.py pour détecter la langue
  → Français : France, Suisse romande (Genève, Lausanne, Fribourg, Sion...),
    Belgique francophone (Bruxelles, Liège, Namur...), Québec, Afrique francophone
  → Anglais : Finlande, UK, Irlande, USA, Australie, et par défaut
  → Le sujet, le corps HTML, le texte brut, les boutons ET les mailto
    sont TOUS traduits automatiquement via le dict TRANSLATIONS
  → Pour ajouter une langue : ajouter une entrée dans TRANSLATIONS (send_35_promo.py)
    et mettre à jour detect_lang() avec les mots-clés de villes/pays
"""
import json
import os
from datetime import datetime

REGISTRY_FILE = os.path.join(os.path.dirname(__file__), '..', 'promo_emails_sent.json')
REGISTRY_FILE = os.path.abspath(REGISTRY_FILE)


def _load_registry():
    """Charge le registre depuis le fichier JSON."""
    if not os.path.exists(REGISTRY_FILE):
        return {}
    try:
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            if isinstance(data, list):
                return {e.lower().strip(): {"sent_at": "unknown"} for e in data if isinstance(e, str)}
    except (json.JSONDecodeError, IOError):
        pass
    return {}


def _save_registry(registry):
    """Sauvegarde le registre dans le fichier JSON."""
    with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)


def was_already_sent(email):
    """Vérifie si un email promo a déjà été envoyé à cette adresse."""
    if not email:
        return True
    registry = _load_registry()
    return email.lower().strip() in registry


def mark_as_sent(email, script="unknown", context=""):
    """Marque une adresse comme ayant reçu un email promo."""
    if not email:
        return
    registry = _load_registry()
    key = email.lower().strip()
    if key not in registry:
        registry[key] = {
            "sent_at": datetime.utcnow().isoformat(),
            "script": script,
            "context": context
        }
        _save_registry(registry)


def mark_batch_as_sent(emails, script="unknown", context=""):
    """Marque plusieurs adresses comme ayant reçu un email promo."""
    if not emails:
        return
    registry = _load_registry()
    now = datetime.utcnow().isoformat()
    changed = False
    for email in emails:
        if not email:
            continue
        key = email.lower().strip()
        if key not in registry:
            registry[key] = {"sent_at": now, "script": script, "context": context}
            changed = True
    if changed:
        _save_registry(registry)


BLOCKED_PREFIXES = [
    'info@', 'contact@', 'admin@', 'webmaster@', 'noreply@', 'no-reply@',
    'support@', 'hello@', 'office@', 'mail@', 'postmaster@',
    'billing@', 'sales@', 'marketing@', 'press@', 'media@', 'presse@',
    'communication@', 'com@', 'redaction@', 'reservation@', 'reservations@',
    'billetterie@', 'production@', 'evenement@', 'evenements@', 'event@',
    'events@', 'booking@', 'team@', 'equipe@', 'staff@',
    'bibliotheque@', 'mediatheque@', 'libre@', 'opendata@',
    'centresportif@', 'fondation@', 'museu@', 'openschool@',
    'visite@', 'orchestras@', 'stadtpolizei@', 'vereinsekretariat@',
    'accueil@', 'direction@', 'secretariat@', 'comptabilite@',
    'rh@', 'hr@', 'jobs@', 'careers@', 'recrutement@',
    'service@', 'general@', 'bureau@',
]

BLOCKED_DOMAINS = [
    'eventbrite', 'ticketmaster', 'fever', 'eventfrog', 'ra.co', 'dice.fm',
    'shotgun', 'ticketcorner', 'starticket', 'petzi', 'fnac', 'digitick',
    'billetweb', 'mapstr', 'openagenda', 'timeout', 'sortiraparis',
    'infoconcert', 'loisirs.ch', 'agenda.ch', 'tourisme', 'tourism',
    'sortir', 'quefaire', 'lilleattractions', 'rave-party',
    'gmail.com', 'yahoo', 'hotmail', 'outlook.com', 'protonmail',
    'mapevent', 'sorbonne', 'paris.fr', 'hel.fi', 'admin.vs.ch',
    'asso.fr', 'actisce',
]

MAX_CONTACTS_PER_DOMAIN = 3


def is_blocked_email(email):
    """Vérifie si un email est bloqué (générique, concurrent, site promo)."""
    if not email:
        return True, "email vide"
    e = email.lower().strip()
    if '@' not in e:
        return True, "pas un email valide"
    for prefix in BLOCKED_PREFIXES:
        if e.startswith(prefix):
            return True, f"prefixe generique: {prefix}"
    domain = e.split('@')[1]
    for blocked in BLOCKED_DOMAINS:
        if blocked in domain:
            return True, f"domaine bloque: {blocked}"
    return False, "ok"


def _count_domain_in_registry(domain, registry):
    """Compte combien d'emails du même domaine sont déjà dans le registre."""
    count = 0
    for sent_email in registry:
        if '@' in sent_email and sent_email.split('@')[1] == domain:
            count += 1
    return count


def filter_new_recipients(emails):
    """Filtre une liste d'emails: jamais contactés + pas bloqués + limite par domaine."""
    if not emails:
        return []
    registry = _load_registry()
    result = []
    domains_in_batch = {}
    for e in emails:
        if not e:
            continue
        key = e.lower().strip()
        if key in registry:
            continue
        blocked, reason = is_blocked_email(key)
        if blocked:
            continue
        domain = key.split('@')[1] if '@' in key else ''
        already_in_registry = _count_domain_in_registry(domain, registry)
        in_this_batch = domains_in_batch.get(domain, 0)
        if already_in_registry + in_this_batch >= MAX_CONTACTS_PER_DOMAIN:
            continue
        domains_in_batch[domain] = in_this_batch + 1
        result.append(e)
    return result


def get_all_sent():
    """Retourne toutes les adresses déjà contactées."""
    return _load_registry()


def get_sent_count():
    """Retourne le nombre total d'adresses contactées."""
    return len(_load_registry())
