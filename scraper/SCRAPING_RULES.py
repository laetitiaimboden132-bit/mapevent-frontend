"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    RÈGLES DE SCRAPING - MapEventAI                         ║
║                                                                            ║
║   CE FICHIER DOIT ÊTRE IMPORTÉ PAR TOUS LES SCRAPERS                      ║
║   Dernière mise à jour: 2026-02-09                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

RÈGLES LÉGALES ET ÉTHIQUES:
===========================

1. SOURCES AUTORISÉES UNIQUEMENT:
   - Offices du tourisme (valais.ch, myswitzerland.com, geneve.com, vaud.ch, etc.)
   - Sites communaux (geneve.ch, ville-geneve.ch, sion.ch, etc.)
   - Agendas culturels publics (agenda.culturevalais.ch, etc.)
   - Sites dédiés des événements eux-mêmes (palpfestival.ch, etc.)
   
   ⛔ NE JAMAIS scraper:
   - Sites de presse / journaux
   - Réseaux sociaux
   - Plateformes de billetterie privées (eventfrog, ticketmaster, etc.)
   - Sites e-commerce

2. LIMITES PAR SOURCE (RÈGLE FONDAMENTALE):
   - Maximum 25% des events que LE SITE SOURCE propose sur son site
   - PAS 25% de notre total → 25% du TOTAL du site source !
   - Si CGU du site interdit la reproduction → Maximum 15% des events du site
   - Exemple: si un site a 100 events → on prend max 25 (ou 15 si CGU strictes)
   - Exemple: si un site a 11000 events → on prend max 2750 (mais on n'en a jamais besoin d'autant)
   - CALCULER le max AVANT de commencer à scraper
   - Répartir les sources au maximum

3. DÉLAI ENTRE REQUÊTES:
   - Minimum 8 secondes entre chaque requête HTTP
   - Respecter robots.txt
   - User-Agent transparent ("MapEventAI-Bot/1.0")

4. CONTENU:
   - Toujours réécrire les descriptions (pas de copier-coller)
   - Toujours citer la source originale (source_url)
   - Ne jamais inventer d'URL → si on ne trouve pas l'URL exacte de l'event, ne pas le publier
   - Vérifier l'existence réelle de chaque événement

4b. SOURCE_URL (CRITIQUE – PUBLICATION ORIGINALE):
   - source_url = URL de la PAGE DÉDIÉE à cet event uniquement
   - Au clic sur "Voir la publication originale", l'utilisateur doit arriver sur l'event, PAS sur :
     * Page d'accueil / homepage
     * Page liste / agenda
     * Page titre générique
     * Page d'un autre event
   - Si l'URL exacte de l'event n'est pas trouvée → NE PAS publier l'event

4c. CATÉGORIES PAR EVENT SCRAPÉ (MAX 3):
   - 1 catégorie pertinente → 1 seule
   - 2 pertinentes → 2
   - 3 ou plus → garder les 3 les plus pertinentes (max 3)
   - BIEN ANALYSER : titre, description, lieu, type d'event → ne pas mettre n'importe quoi
   - PRIVILÉGIER LES SOUS-SOUS-CATÉGORIES : Acid Techno, Deep House, Blues, Minimal Techno...
     Pas "Electronic" ou "Musique" générique quand une sous-catégorie précise existe.

5. VÉRIFICATION CGU OBLIGATOIRE:
   - Avant de scraper un nouveau site, VÉRIFIER ses CGU / mentions légales
   - Documenter le résultat dans CGU_REGISTRY ci-dessous
"""

# ============================================================================
# REGISTRE DES CGU VÉRIFIÉES
# ============================================================================
# Chaque source doit être documentée ici AVANT de scraper

CGU_REGISTRY = {
    # ---- SOURCES INTERDITES (Niveau 1-2) ----
    "www.geneve.ch": {
        "type": "SITE COMMUNAL",
        "cgu_url": "https://www.geneve.ch/mentions-legales",
        "cgu_status": "INTERDIT",
        "cgu_detail": "CGU: 'La reproduction, la transmission, la modification ou l'utilisation à des fins publiques ou commerciales sont soumises à autorisation écrite préalable.' Niveau 2 RISQUE ÉLEVÉ.",
        "max_percentage": 0,
        "verified_date": "2026-02-09",
        "is_public_source": True,
    },
    "evenements.geneve.ch": {
        "type": "SITE COMMUNAL",
        "cgu_url": "https://www.geneve.ch/mentions-legales",
        "cgu_status": "INTERDIT",
        "cgu_detail": "Même CGU que geneve.ch - autorisation écrite requise. Niveau 2.",
        "max_percentage": 0,
        "verified_date": "2026-02-09",
        "is_public_source": True,
    },
    "www.morges.ch": {
        "type": "SITE COMMUNAL",
        "cgu_url": None,
        "cgu_status": "INTERDIT",
        "cgu_detail": "robots.txt bloque explicitement ClaudeBot, GPTBot, anthropic-ai et tous bots IA. Niveau 2 RISQUE ÉLEVÉ.",
        "max_percentage": 0,
        "verified_date": "2026-02-09",
        "is_public_source": True,
    },

    # ---- OFFICES DU TOURISME ----
    "www.valais.ch": {
        "type": "OFFICE TOURISME",
        "cgu_url": "https://www.valais.ch/fr/informations/conditions-generales",
        "cgu_status": "RESTRICTIVE",
        "cgu_detail": "Section XVIII: 'Toute utilisation en dehors de l'usage personnel admis par la loi est interdite, à moins que VWP n'ait expressément donné son accord par écrit'",
        "max_percentage": 15,
        "verified_date": "2026-02-08",
        "is_public_source": True,
    },
    "www.myswitzerland.com": {
        "type": "OFFICE TOURISME",
        "cgu_url": "https://www.myswitzerland.com/fr-ch/planification/vie-pratique/imprint/",
        "cgu_status": "STANDARD",
        "cgu_detail": "Suisse Tourisme, corporation publique. Pas de restriction explicite sur la reproduction d'infos événementielles. Mention source recommandée.",
        "max_percentage": 30,
        "verified_date": "2026-02-08",
        "is_public_source": True,
    },
    "www.geneve.com": {
        "type": "OFFICE TOURISME",
        "cgu_url": None,
        "cgu_status": "NON_TROUVÉE",
        "cgu_detail": "Genève Tourisme. CGU non trouvée. Appliquer max 15% par précaution.",
        "max_percentage": 15,
        "verified_date": "2026-02-08",
        "is_public_source": True,
    },
    "www.vaud.ch": {
        "type": "OFFICE TOURISME",
        "cgu_url": None,
        "cgu_status": "NON_TROUVÉE",
        "cgu_detail": "Canton de Vaud, site officiel. CGU non trouvée. Appliquer max 15% par précaution.",
        "max_percentage": 15,
        "verified_date": "2026-02-08",
        "is_public_source": True,
    },
    "www.montreuxriviera.com": {
        "type": "OFFICE TOURISME",
        "cgu_url": None,
        "cgu_status": "NON_TROUVÉE",
        "cgu_detail": "Office du tourisme Montreux Riviera. CGU non trouvée. Appliquer max 15% par précaution.",
        "max_percentage": 15,
        "verified_date": "2026-02-08",
        "is_public_source": True,
    },

    # ---- SITES COMMUNAUX ----
    "www.geneve.ch": {
        "type": "SITE COMMUNAL",
        "cgu_url": "https://www.geneve.ch/fr/mentions-legales",
        "cgu_status": "RESTRICTIVE",
        "cgu_detail": "Mentions légales: 'La reproduction, la transmission, la modification ou l'utilisation à des fins publiques ou commerciales du contenu protégé par les droits d'auteur sont soumises à autorisation écrite préalable de la Ville de Genève'",
        "max_percentage": 15,
        "verified_date": "2026-02-08",
        "is_public_source": True,
    },
    "www.ville-geneve.ch": {
        "type": "SITE COMMUNAL",
        "cgu_url": None,
        "cgu_status": "NON_TROUVÉE",
        "cgu_detail": "Ville de Genève, probablement mêmes CGU que geneve.ch. Appliquer max 15%.",
        "max_percentage": 15,
        "verified_date": "2026-02-08",
        "is_public_source": True,
    },
    "evenements.geneve.ch": {
        "type": "SITE COMMUNAL",
        "cgu_url": None,
        "cgu_status": "NON_TROUVÉE",
        "cgu_detail": "Sous-domaine de geneve.ch. Mêmes CGU restrictives.",
        "max_percentage": 15,
        "verified_date": "2026-02-08",
        "is_public_source": True,
    },

    # ---- AGENDAS CULTURELS ----
    "agenda.culturevalais.ch": {
        "type": "AGENDA CULTUREL PUBLIC",
        "cgu_url": "https://www.vs-myculture.ch/legal",
        "cgu_status": "STANDARD",
        "cgu_detail": "Géré par le Service de la culture du Canton du Valais (institution publique). Agenda conçu pour promouvoir les événements culturels. Pas de restriction explicite sur le partage d'infos événementielles.",
        "max_percentage": 30,
        "verified_date": "2026-02-08",
        "is_public_source": True,
    },
    "www.tempslibre.ch": {
        "type": "AGENDA CULTUREL PRIVÉ",
        "cgu_url": None,
        "cgu_status": "NON_TROUVÉE",
        "cgu_detail": "Opéré par GeneralMedia SA (privé). Parent letemps.ch interdit extraction automatisée. RISQUE JURIDIQUE. Max 15% par précaution.",
        "max_percentage": 15,
        "verified_date": "2026-02-08",
        "is_public_source": False,  # Privé
        "risk_level": "MOYEN",
    },
    "vd.leprogramme.ch": {
        "type": "AGENDA CULTUREL PRIVÉ",
        "cgu_url": None,
        "cgu_status": "NON_TROUVÉE",
        "cgu_detail": "Plateforme privée d'agenda culturel. CGU non trouvée. Appliquer max 15% par précaution.",
        "max_percentage": 15,
        "verified_date": "2026-02-08",
        "is_public_source": False,  # Privé
        "risk_level": "MOYEN",
    },

    # ---- INSTITUTIONS CULTURELLES ----
    "www.elysee.ch": {
        "type": "INSTITUTION CULTURELLE",
        "cgu_url": None,
        "cgu_status": "NON_TROUVÉE",
        "cgu_detail": "Musée Photo Elysée, institution publique. Appliquer max 15% par précaution.",
        "max_percentage": 15,
        "verified_date": "2026-02-08",
        "is_public_source": True,
    },
    "home.cern": {
        "type": "INSTITUTION SCIENTIFIQUE",
        "cgu_url": None,
        "cgu_status": "NON_TROUVÉE",
        "cgu_detail": "Organisation internationale. Event CERN Open Days. Appliquer max 15%.",
        "max_percentage": 15,
        "verified_date": "2026-02-08",
        "is_public_source": True,
    },

    # ---- SITES DÉDIÉS DES ÉVÉNEMENTS (site propre de l'event) ----
    # Ces sites sont les sites OFFICIELS des événements eux-mêmes.
    # Ce sont les meilleures sources: l'organisateur publie son propre event.
    # Risque juridique: MINIMAL (promotion souhaitée par l'organisateur)
    "www.lakeparade.ch": {"type": "SITE EVENT DÉDIÉ", "cgu_status": "SITE_PROPRE", "max_percentage": 30, "verified_date": "2026-02-08", "is_public_source": True},
    "www.giff.ch": {"type": "SITE EVENT DÉDIÉ", "cgu_status": "SITE_PROPRE", "max_percentage": 30, "verified_date": "2026-02-08", "is_public_source": True},
    "www.escalade.ch": {"type": "SITE EVENT DÉDIÉ", "cgu_status": "SITE_PROPRE", "max_percentage": 30, "verified_date": "2026-02-08", "is_public_source": True},
    "www.generaligenevemarathon.com": {"type": "SITE EVENT DÉDIÉ", "cgu_status": "SITE_PROPRE", "max_percentage": 30, "verified_date": "2026-02-08", "is_public_source": True},
    "www.batie.ch": {"type": "SITE EVENT DÉDIÉ", "cgu_status": "SITE_PROPRE", "max_percentage": 30, "verified_date": "2026-02-08", "is_public_source": True},
    "www.watchesandwonders.com": {"type": "SITE EVENT DÉDIÉ", "cgu_status": "SITE_PROPRE", "max_percentage": 30, "verified_date": "2026-02-08", "is_public_source": True},
    "www.genevetriathlon.ch": {"type": "SITE EVENT DÉDIÉ", "cgu_status": "SITE_PROPRE", "max_percentage": 30, "verified_date": "2026-02-08", "is_public_source": True},
    "www.antigel.ch": {"type": "SITE EVENT DÉDIÉ", "cgu_status": "SITE_PROPRE", "max_percentage": 30, "verified_date": "2026-02-08", "is_public_source": True},
    "nuitdesmusees-geneve.ch": {"type": "SITE EVENT DÉDIÉ", "cgu_status": "SITE_PROPRE", "max_percentage": 30, "verified_date": "2026-02-08", "is_public_source": True},
    "www.inventions-geneva.ch": {"type": "SITE EVENT DÉDIÉ", "cgu_status": "SITE_PROPRE", "max_percentage": 30, "verified_date": "2026-02-08", "is_public_source": True},
    "www.genevelux.ch": {"type": "SITE EVENT DÉDIÉ", "cgu_status": "SITE_PROPRE", "max_percentage": 30, "verified_date": "2026-02-08", "is_public_source": True},
    "www.boldormirabaud.ch": {"type": "SITE EVENT DÉDIÉ", "cgu_status": "SITE_PROPRE", "max_percentage": 30, "verified_date": "2026-02-08", "is_public_source": True},
    "www.lavaux-passion.ch": {"type": "SITE EVENT DÉDIÉ", "cgu_status": "SITE_PROPRE", "max_percentage": 30, "verified_date": "2026-02-08", "is_public_source": True},
    "www.ultratourmonterosa.com": {"type": "SITE EVENT DÉDIÉ", "cgu_status": "SITE_PROPRE", "max_percentage": 30, "verified_date": "2026-02-08", "is_public_source": True},
    "swisspeaks.ch": {"type": "SITE EVENT DÉDIÉ", "cgu_status": "SITE_PROPRE", "max_percentage": 30, "verified_date": "2026-02-08", "is_public_source": True},
    "carnavaldemonthey.com": {"type": "SITE EVENT DÉDIÉ", "cgu_status": "SITE_PROPRE", "max_percentage": 30, "verified_date": "2026-02-08", "is_public_source": True},
    "palpfestival.ch": {"type": "SITE EVENT DÉDIÉ", "cgu_status": "SITE_PROPRE", "max_percentage": 30, "verified_date": "2026-02-08", "is_public_source": True},
    "www.raceherens.ch": {"type": "SITE EVENT DÉDIÉ", "cgu_status": "SITE_PROPRE", "max_percentage": 30, "verified_date": "2026-02-08", "is_public_source": True},
    "www.foireduvalais.ch": {"type": "SITE EVENT DÉDIÉ", "cgu_status": "SITE_PROPRE", "max_percentage": 30, "verified_date": "2026-02-08", "is_public_source": True},

    # ---- NOUVEAUX SITES (ajoutés 2026-02-09) ----
    "www.sierre.ch": {
        "type": "SITE COMMUNAL",
        "cgu_url": None,
        "cgu_status": "STANDARD",
        "cgu_detail": "Site communal de Sierre, agenda public. 133 events total.",
        "max_percentage": 25,
        "verified_date": "2026-02-09",
        "is_public_source": True,
    },
    "www.casanovamonthey.ch": {
        "type": "OFFICE CULTUREL",
        "cgu_url": None,
        "cgu_status": "STANDARD",
        "cgu_detail": "Office culturel municipal de Monthey. Agenda public. 57 events total.",
        "max_percentage": 25,
        "verified_date": "2026-02-09",
        "is_public_source": True,
    },
    "lesgenevois.com": {
        "type": "AGENDA COMMUNAUTAIRE",
        "cgu_url": None,
        "cgu_status": "NON_TROUVÉE",
        "cgu_detail": "Agenda communautaire genevois. CGU non trouvée. Appliquer 15% par précaution.",
        "max_percentage": 15,
        "verified_date": "2026-02-09",
        "is_public_source": False,
        "risk_level": "MOYEN",
    },
    "www.morges.ch": {
        "type": "SITE COMMUNAL",
        "cgu_url": "https://www.morges.ch/page/mentions-legales-200365",
        "cgu_status": "RESTRICTIVE",
        "cgu_detail": "Reproduction soumise à autorisation écrite préalable. 34 events total.",
        "max_percentage": 15,
        "verified_date": "2026-02-09",
        "is_public_source": True,
    },

    # ---- SOURCES INTERDITES SUISSE (Niveau 2) ----
    "www.sion.ch": {
        "type": "SITE COMMUNAL",
        "cgu_url": "https://www.sion.ch/mentions-legales",
        "cgu_status": "INTERDIT",
        "cgu_detail": "CGU: 'Pour toute reproduction, le consentement écrit du titulaire du droit d'auteur doit être obtenu'. Niveau 2 RISQUE ÉLEVÉ.",
        "max_percentage": 0,
        "verified_date": "2026-02-09",
        "is_public_source": True,
    },
    "www.crans-montana.ch": {
        "type": "OFFICE TOURISME",
        "cgu_url": None,
        "cgu_status": "INTERDIT",
        "cgu_detail": "robots.txt: Disallow: / pour User-agent: *. Contradictoire avec Allow pour AI bots. Crawl-delay: 15s. Trop risqué.",
        "max_percentage": 0,
        "verified_date": "2026-02-09",
        "is_public_source": True,
    },

    # ---- NOUVELLES SOURCES SÛRES SUISSE (Niveau 4) ----
    "l-agenda.ch": {
        "type": "AGENDA CULTUREL PUBLIC",
        "cgu_url": None,
        "cgu_status": "STANDARD",
        "cgu_detail": "Agenda culturel Suisse romande. robots.txt: Disallow /wp-admin/ uniquement. 500+ events.",
        "max_percentage": 30,
        "verified_date": "2026-02-09",
        "is_public_source": True,
    },
    "www.martigny.ch": {
        "type": "SITE COMMUNAL",
        "cgu_url": None,
        "cgu_status": "STANDARD",
        "cgu_detail": "Site communal de Martigny. robots.txt: Disallow /wp/wp-admin/ uniquement. 30-50 events.",
        "max_percentage": 30,
        "verified_date": "2026-02-09",
        "is_public_source": True,
    },
    "www.musees-valais.ch": {
        "type": "INSTITUTION CULTURELLE",
        "cgu_url": None,
        "cgu_status": "STANDARD",
        "cgu_detail": "Musées Cantonaux du Valais. robots.txt: Disallow /wp-admin/ uniquement. 30-50 events.",
        "max_percentage": 30,
        "verified_date": "2026-02-09",
        "is_public_source": True,
    },
    "www.verbier.ch": {
        "type": "OFFICE TOURISME",
        "cgu_url": None,
        "cgu_status": "STANDARD",
        "cgu_detail": "Office du Tourisme Verbier. robots.txt: blocage chemins techniques uniquement. 20-30 events.",
        "max_percentage": 30,
        "verified_date": "2026-02-09",
        "is_public_source": True,
    },
    "www.gianadda.ch": {
        "type": "INSTITUTION CULTURELLE",
        "cgu_url": "https://www.gianadda.ch/accueil/infos_pratiques/mentions-legales/",
        "cgu_status": "STANDARD",
        "cgu_detail": "Fondation Pierre Gianadda, institution culturelle majeure de Martigny. Site propre de la fondation.",
        "max_percentage": 30,
        "verified_date": "2026-02-09",
        "is_public_source": True,
    },

    # ---- NOUVELLES SOURCES HAUTE-SAVOIE FRANCE ----
    "www.thononlesbains.com": {
        "type": "OFFICE TOURISME FRANCE",
        "cgu_url": None,
        "cgu_status": "STANDARD",
        "cgu_detail": "Office du Tourisme Thonon-les-Bains. robots.txt: Disallow /cms/wp-admin/ uniquement. 102 events. NIVEAU 4.",
        "max_percentage": 30,
        "verified_date": "2026-02-09",
        "is_public_source": True,
    },
    "www.lac-in-blue.com": {"type": "SITE EVENT DÉDIÉ FRANCE", "cgu_status": "SITE_PROPRE", "max_percentage": 30, "verified_date": "2026-02-09", "is_public_source": True},
    "bonlieu-annecy.com": {"type": "INSTITUTION CULTURELLE FRANCE", "cgu_status": "STANDARD", "max_percentage": 30, "verified_date": "2026-02-09", "is_public_source": True},
    "www.annecyfestival.com": {"type": "SITE EVENT DÉDIÉ FRANCE", "cgu_status": "SITE_PROPRE", "max_percentage": 30, "verified_date": "2026-02-09", "is_public_source": True},

    # ---- SOURCES FRANÇAISES RISQUE MODÉRÉ (Niveau 3) ----
    "www.hautesavoiemontblanc-tourisme.com": {
        "type": "OFFICE TOURISME FRANCE",
        "cgu_url": None,
        "cgu_status": "RESTRICTIVE",
        "cgu_detail": "Usage commercial interdit, usage personnel autorisé avec citation source. 100+ events.",
        "max_percentage": 15,
        "verified_date": "2026-02-09",
        "is_public_source": True,
    },
    "www.megeve-tourisme.fr": {
        "type": "OFFICE TOURISME FRANCE",
        "cgu_url": None,
        "cgu_status": "RESTRICTIVE",
        "cgu_detail": "Usage commercial interdit, usage personnel/associatif autorisé. Crawl-delay: 5s. 1900+ events.",
        "max_percentage": 15,
        "verified_date": "2026-02-09",
        "is_public_source": True,
    },

    # ---- SOURCES FRANÇAISES INTERDITES ----
    "lac-annecy.com": {
        "type": "OFFICE TOURISME FRANCE",
        "cgu_url": None,
        "cgu_status": "INTERDIT",
        "cgu_detail": "Reproduction interdite sans autorisation écrite.",
        "max_percentage": 0,
        "verified_date": "2026-02-09",
        "is_public_source": True,
    },
    "chamonix.com": {
        "type": "OFFICE TOURISME FRANCE",
        "cgu_url": None,
        "cgu_status": "INTERDIT",
        "cgu_detail": "Usage commercial interdit.",
        "max_percentage": 0,
        "verified_date": "2026-02-09",
        "is_public_source": True,
    },

    # ---- PLATEFORMES PRIVÉES (à éviter) ----
    "eventfrog.ch": {
        "type": "PLATEFORME BILLETTERIE PRIVÉE",
        "cgu_url": None,
        "cgu_status": "INTERDIT",
        "cgu_detail": "Plateforme de billetterie privée. NE PAS SCRAPER.",
        "max_percentage": 0,
        "verified_date": "2026-02-08",
        "is_public_source": False,
        "risk_level": "ÉLEVÉ",
    },
}

# ============================================================================
# LIMITES ACTUELLES PAR SOURCE (après audit du 2026-02-08)
# ============================================================================

CURRENT_DISTRIBUTION = {
    # Source: (nb_events_chez_nous, nb_total_sur_le_site, pct_du_site, statut)
    "agenda.culturevalais.ch":       (51, "~300", "~17%", "OK - institution publique, max 30%"),
    "www.sierre.ch":                 (19, 133, "14.3%", "OK - site communal, max 30%"),
    "www.morges-tourisme.ch":        (13, "~50", "~26%", "OK - reproduction libre, max 80%"),
    "lesgenevois.com":               (8, 228, "3.5%", "OK - CGU non trouvée, max 15%"),
    "www.casanovamonthey.ch":        (4, 57, "7%", "OK - office culturel, max 30%"),
    "www.myswitzerland.com":         (4, "milliers", "<1%", "OK - office tourisme, max 30%"),
    "www.palexpo.ch":                (3, "centaines", "<1%", "OK"),
    "www.gianadda.ch":               (1, "~10", "~10%", "OK - institution culturelle"),
    "www.lac-in-blue.com":           (6, 6, "100%", "OK - site propre du festival"),
    "bonlieu-annecy.com":            (2, "~50", "~4%", "OK - scène nationale"),
    "www.thononlesbains.com":        (1, 102, "~1%", "OK - office tourisme France, max 30%"),
    "www.annecyfestival.com":        (1, 1, "100%", "OK - site propre du festival"),
    "sites_dédiés":                  (82, "N/A", "N/A", "Sites propres des events"),
}

# Total: 195 events (mise à jour 2026-02-09)
# Régions: Valais 98, Vaud 48, Genève 35, Haute-Savoie (France) 10, Autre CH 4
#
# SOURCES INTERDITES (vérifiées et supprimées):
# - www.geneve.ch / evenements.geneve.ch : Niveau 2 - CGU exige autorisation écrite
# - www.morges.ch : Niveau 2 - robots.txt bloque ClaudeBot et AI bots
# - www.sion.ch : Niveau 2 - CGU exige consentement écrit pour reproduction
# - www.crans-montana.ch : Niveau 2 - robots.txt contradictoire (Disallow: /)
# - lac-annecy.com : Niveau 1 - Reproduction interdite sans autorisation
# - chamonix.com : Niveau 1 - Usage commercial interdit
#
# NOUVELLES SOURCES SÛRES identifiées (à exploiter):
# - l-agenda.ch : 500+ events Romandie (Niveau 4)
# - www.martigny.ch : 30-50 events Valais (Niveau 4)
# - www.musees-valais.ch : 30-50 events Valais (Niveau 4)
# - www.verbier.ch : 20-30 events Valais (Niveau 4)

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

import time
import random

# Délai minimum entre requêtes (en secondes)
MIN_REQUEST_DELAY = 8

def respectful_delay():
    """Attend entre 8 et 12 secondes entre les requêtes."""
    delay = MIN_REQUEST_DELAY + random.uniform(0, 4)
    time.sleep(delay)

def check_source_allowed(domain: str) -> dict:
    """
    Vérifie si un domaine est autorisé pour le scraping.
    Retourne un dict avec les infos de conformité.
    """
    if domain in CGU_REGISTRY:
        info = CGU_REGISTRY[domain]
        return {
            "allowed": info["cgu_status"] != "INTERDIT",
            "max_percentage": info["max_percentage"],
            "type": info["type"],
            "cgu_status": info["cgu_status"],
            "warning": info.get("cgu_detail", ""),
        }
    else:
        return {
            "allowed": False,
            "max_percentage": 0,
            "type": "INCONNU",
            "cgu_status": "NON_VÉRIFIÉ",
            "warning": f"CGU NON VÉRIFIÉE pour {domain}. Vérifier avant de scraper!",
        }

def get_max_events_for_source(domain: str, total_events_on_source_site: int) -> int:
    """
    Calcule le nombre maximum d'events autorisés depuis une source.
    
    IMPORTANT: total_events_on_source_site = nombre total d'events SUR LE SITE SOURCE
    PAS notre total d'events !
    
    Exemple: si le site a 100 events et max_percentage=25% → on peut prendre 25 events max
    """
    info = check_source_allowed(domain)
    max_pct = info["max_percentage"]
    return int(total_events_on_source_site * max_pct / 100)

def validate_scraping_plan(planned_events: dict, current_total: int) -> list:
    """
    Valide un plan de scraping avant exécution.
    
    Args:
        planned_events: dict {domain: nb_events_à_ajouter}
        current_total: nombre total d'events actuels
    
    Returns:
        Liste de warnings/erreurs
    """
    issues = []
    new_total = current_total + sum(planned_events.values())
    
    for domain, count in planned_events.items():
        info = check_source_allowed(domain)
        
        if not info["allowed"]:
            issues.append(f"ERREUR: {domain} - source non autorisée ({info['cgu_status']})")
            continue
        
        max_allowed = get_max_events_for_source(domain, new_total)
        
        # Compter les events existants de cette source
        existing = CURRENT_DISTRIBUTION.get(domain, (0,))[0]
        total_from_source = existing + count
        
        if total_from_source > max_allowed:
            issues.append(
                f"ATTENTION: {domain} - {total_from_source} events prévu "
                f"(max {max_allowed} = {info['max_percentage']}% de {new_total})"
            )
    
    return issues


# ============================================================================
# HEADERS POUR REQUÊTES
# ============================================================================

SCRAPER_HEADERS = {
    "User-Agent": "MapEventAI-Bot/1.0 (+https://mapevent.ai; contact@mapevent.ai)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "fr-CH,fr;q=0.9",
}
