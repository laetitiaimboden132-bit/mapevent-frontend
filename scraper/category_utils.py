#!/usr/bin/env python3
"""
Module partage de categorisation d'evenements.
Utilise des regex word boundaries pour eviter les faux positifs.

Usage:
    from category_utils import assign_categories
    cats = assign_categories(title, description, keywords, location)
"""

import re


def _word_in(word, text):
    """Verifie si un mot est present comme mot entier (word boundary)."""
    return bool(re.search(r'\b' + re.escape(word) + r'\b', text, re.IGNORECASE))


def _any_word_in(words, text):
    """Verifie si un des mots est present comme mot entier."""
    return any(_word_in(w, text) for w in words)


def _substr_in(substr, text):
    """Simple substring match (pour les prefixes comme 'symphoni')."""
    return substr in text


def assign_categories(title, description='', keywords='', location_name=''):
    """
    Assigne des categories a un evenement.
    Version amelioree avec word boundaries et regles anti-faux-positifs.
    """
    title_lower = (title or '').lower()
    desc_lower = (description or '').lower()
    kw_lower = (keywords or '').lower()
    loc_lower = (location_name or '').lower()
    
    # Texte complet pour recherche
    text = f"{title_lower} {desc_lower} {kw_lower} {loc_lower}"
    
    result = []
    
    # ===========================================================
    # DETECTION DU TYPE D'EVENEMENT (priorite aux non-musicaux)
    # ===========================================================
    
    is_sport = False
    is_expo = False
    is_cinema = False
    is_theatre = False
    is_conference = False
    
    # --- SPORTS ---
    sport_words = {
        'ski': 'Sport > Glisse', 'snowboard': 'Sport > Glisse',
        'patinage': 'Sport > Glisse', 'luge': 'Sport > Glisse',
        'hockey': 'Sport > Terrestre', 'football': 'Sport > Terrestre',
        'tennis': 'Sport > Terrestre', 'basket': 'Sport > Terrestre',
        'rugby': 'Sport > Terrestre', 'volley': 'Sport > Terrestre',
        'handball': 'Sport > Terrestre',
        'golf': 'Sport > Terrestre',
        'trail': 'Sport > Terrestre', 'marathon': 'Sport > Terrestre',
        'triathlon': 'Sport > Terrestre',
        'cyclisme': 'Sport > Terrestre',
        'vtt': 'Sport > Terrestre', 'escalade': 'Sport > Terrestre',
        'boxe': 'Sport > Terrestre', 'judo': 'Sport > Terrestre',
        'escrime': 'Sport > Terrestre',
        'natation': 'Sport > Aquatique',
        'kayak': 'Sport > Aquatique', 'voile': 'Sport > Aquatique',
        'aviron': 'Sport > Aquatique',
        'parapente': 'Sport > Aérien',
    }
    for word, cat in sport_words.items():
        if _word_in(word, text) and cat not in result:
            result.append(cat)
            is_sport = True
    
    # Mots sport generiques
    if _any_word_in(['compétition sportive', 'tournoi', 'championnat', 'multisports'], text):
        if not is_sport:
            result.append('Sport > Terrestre')
            is_sport = True
    
    # "vs" dans le titre -> probablement un match
    if re.search(r'\bvs\.?\b', title_lower, re.IGNORECASE):
        if not is_sport and not _any_word_in(['dj', 'concert', 'jazz', 'techno', 'electro'], text):
            if not any('Sport' in c for c in result):
                result.append('Sport > Terrestre')
            is_sport = True
    
    # Mots sport avec word boundary (eviter "randonnée" dans d'autres contextes)
    if _any_word_in(['randonnée', 'course à pied'], text):
        if 'Sport > Terrestre' not in result:
            result.append('Sport > Terrestre')
            is_sport = True
    if _word_in('yoga', text):
        if 'Sport > Terrestre' not in result:
            result.append('Sport > Terrestre')
    if _any_word_in(['vélo', 'bike', 'cycling'], text):
        if 'Sport > Terrestre' not in result:
            result.append('Sport > Terrestre')
    
    # --- CINEMA ---
    if _any_word_in(['cinéma', 'cinema', 'projection', 'documentaire'], text):
        result.append('Culture > Cinéma')
        is_cinema = True
    # "film" doit etre un mot entier
    if _word_in('film', text):
        if 'Culture > Cinéma' not in result:
            result.append('Culture > Cinéma')
            is_cinema = True
    
    # --- EXPOSITION ---
    if _any_word_in(['exposition', 'vernissage', 'art contemporain'], text):
        result.append('Culture > Exposition')
        is_expo = True
    if _substr_in('expo ', text) or _substr_in("l'expo", text):
        if 'Culture > Exposition' not in result:
            result.append('Culture > Exposition')
            is_expo = True
    if _any_word_in(['musée', 'museum', 'galerie'], text):
        if 'Culture > Exposition' not in result:
            result.append('Culture > Exposition')
            is_expo = True
    
    # --- THEATRE / SPECTACLE ---
    if _any_word_in(['théâtre', 'theatre', 'theater'], text):
        result.append('Culture > Théâtre')
        is_theatre = True
    if _any_word_in(['comédie', 'tragédie'], text):
        # Attention: "comédie musicale" est musical
        if not _substr_in('comédie musicale', text):
            if 'Culture > Théâtre' not in result:
                result.append('Culture > Théâtre')
                is_theatre = True
    
    if _any_word_in(['danse', 'ballet', 'chorégraphie'], text):
        result.append('Culture > Danse')
    if _any_word_in(['cirque', 'acrobate', 'clown'], text):
        result.append('Culture > Cirque')
    if _any_word_in(['marionnette', 'puppet'], text):
        result.append('Culture > Marionnettes')
    if _any_word_in(['humour', 'humoriste', 'stand-up', 'standup', 'sketch'], text):
        result.append('Culture > Humour')
    if _substr_in('one man show', text) or _substr_in('one-man-show', text):
        if 'Culture > Humour' not in result:
            result.append('Culture > Humour')
    
    # --- CONFERENCE ---
    if _any_word_in(['conférence', 'conference', 'séminaire', 'colloque', 'symposium'], text):
        result.append('Conférence')
        is_conference = True
    if _any_word_in(['débat', 'table ronde'], text):
        if 'Conférence' not in result:
            result.append('Conférence')
            is_conference = True
    
    # --- LITTERATURE / CONTE ---
    if _any_word_in(['conte', 'contes', 'conteur', 'conteuse'], text):
        result.append('Culture > Conte')
    if _any_word_in(['littérature', 'poésie', 'slam'], text):
        result.append('Culture > Littérature')
    if _word_in('lecture', text) and not _any_word_in(['lecture musicale'], text):
        if 'Culture > Littérature' not in result:
            result.append('Culture > Littérature')
    
    # --- PHOTOGRAPHIE ---
    if _any_word_in(['photographie', 'photographe'], text):
        result.append('Culture > Photographie')
    
    # --- VISITE / PATRIMOINE ---
    if _any_word_in(['visite guidée', 'visite commentée', 'patrimoine'], text):
        result.append('Culture > Visite')
    
    # --- GASTRONOMIE ---
    if _any_word_in(['dégustation', 'vignoble', 'vigneron', 'oenologie'], text):
        result.append('Gastronomie > Dégustation vin')
    elif _any_word_in(['bière', 'brasserie'], text):
        result.append('Gastronomie > Dégustation bière')
    elif _any_word_in(['brunch', 'gastronomie', 'culinaire', 'cuisine', 'food'], text):
        result.append('Gastronomie')
    
    # --- MARCHES ---
    if _any_word_in(['brocante', 'vide-grenier'], text):
        result.append('Marché > Brocante')
    elif _word_in('marché', text):
        result.append('Marché')
    if _any_word_in(['foire', 'salon'], text):
        result.append('Foire')
    
    # --- CARNAVAL ---
    if _word_in('carnaval', text):
        result.append('Carnaval')
    if _any_word_in(['parade', 'cortège', 'défilé'], text):
        result.append('Parade')
    
    # --- ATELIER ---
    if _any_word_in(['atelier', 'workshop'], text):
        result.append('Atelier')
    
    # --- FAMILLE ---
    if _any_word_in(['enfant', 'jeune public', 'familial', 'famille'], text):
        result.append('Famille')
    
    # --- DROITS HUMAINS / SOLIDARITE ---
    if _any_word_in(['droits humains', "droits de l'homme", 'humanitaire'], text):
        result.append('Solidarité')
    
    # --- FESTIVAL ---
    if _word_in('festival', text):
        if 'Festival' not in result:
            result.append('Festival')
    
    # ===========================================================
    # MUSIQUE - Seulement si l'evenement semble vraiment musical
    # ===========================================================
    
    # Exclusions: ne PAS ajouter de categories musique si c'est clairement autre chose
    # SAUF si le titre contient explicitement un mot musical fort
    
    title_has_strong_music = _any_word_in([
        'concert', 'dj', 'recital', 'récital', 'orchestre', 'orchestra',
        'symphonie', 'opéra', 'opera', 'karaoké', 'karaoke',
        'jam session', 'spectacle musical', 'comédie musicale',
    ], title_lower)
    
    # Mots musicaux detectes par word boundary
    music_detections = []
    
    # Genres specifiques - utiliser word boundary
    genre_map = [
        (['jazz'], 'Musique > Jazz'),
        (['blues'], 'Musique > Blues'),
        (['rock'], 'Musique > Rock'),
        (['metal'], 'Musique > Metal'),
        (['punk'], 'Musique > Punk'),
        (['techno'], 'Musique > Techno'),
        (['electro'], 'Musique > Electro'),
        (['trance'], 'Musique > Trance'),
        (['reggae'], 'Musique > Reggae'),
        (['hip hop', 'hip-hop'], 'Musique > Hip-Hop'),
        (['salsa', 'bachata'], 'Musique > Latin'),
        (['folk'], 'Musique > Folk'),
        (['gospel'], 'Musique > Gospel'),
        (['world music', 'musiques du monde'], 'Musique > World'),
        (['chanson'], 'Musique > Chanson'),
    ]
    
    for words, cat in genre_map:
        if _any_word_in(words, text):
            music_detections.append(cat)
    
    # Genres par substring (prefixes)
    substr_genre_map = [
        ('symphoni', 'Musique > Classique'),
        ('philharmon', 'Musique > Classique'),
    ]
    for substr, cat in substr_genre_map:
        if _substr_in(substr, text) and cat not in music_detections:
            music_detections.append(cat)
    
    # Mots classiques avec word boundary
    if _any_word_in(['orchestre', 'orchestra', 'opéra', 'opera', 'chorale', 'choeur'], text):
        if 'Musique > Classique' not in music_detections:
            music_detections.append('Musique > Classique')
    
    # "classique" - attention a "voiture classique", "rallye classique"
    if _word_in('classique', text):
        if not _any_word_in(['voiture classique', 'rallye classique', 'style classique'], text):
            if 'Musique > Classique' not in music_detections:
                music_detections.append('Musique > Classique')
    
    # Soul/Funk avec word boundary (eviter "soulèvement")
    if _word_in('soul', text):
        # Exclure "soulèvement", "soulager", "soulier"
        if not _any_word_in(['soulèvement', 'soulèvements', 'soulager', 'soulier'], text):
            if 'Musique > Soul' not in music_detections:
                music_detections.append('Musique > Soul')
    if _word_in('funk', text):
        if 'Musique > Funk' not in music_detections:
            music_detections.append('Musique > Funk')
    
    # "pop" avec word boundary (eviter "pop-up", "population")
    if _word_in('pop', text):
        if not _any_word_in(['pop-up', 'popup', 'popcorn', 'population'], text):
            if 'Musique > Pop' not in music_detections:
                music_detections.append('Musique > Pop')
    
    # "rap" avec word boundary (eviter "drap", "trappe")
    if _word_in('rap', text):
        if not _any_word_in(['drap', 'trappe', 'attrape'], text):
            if 'Musique > Rap' not in music_detections:
                music_detections.append('Musique > Rap')
    
    # "house" avec prudence (eviter "house" en anglais general)
    if _word_in('house', text):
        # Seulement si contexte musical
        if _any_word_in(['house music', 'deep house', 'tech house', 'acid house'], text):
            if 'Musique > House' not in music_detections:
                music_detections.append('Musique > House')
    
    # Concert / musique generique
    concert_detected = False
    if _any_word_in(['concert', 'recital', 'récital', 'jam session', 'karaoké', 'karaoke'], text):
        concert_detected = True
    if _substr_in('spectacle musical', text) or _substr_in('comédie musicale', text):
        concert_detected = True
    
    # DJ avec word boundary
    if re.search(r'\bdj\b', text, re.IGNORECASE):
        if 'Musique > Electro' not in music_detections:
            music_detections.append('Musique > Electro')
        concert_detected = True
    
    # ===========================================================
    # REGLES ANTI-FAUX-POSITIFS POUR LA MUSIQUE
    # ===========================================================
    
    # Si c'est clairement un sport, cinema, expo ou conference
    # -> ne PAS ajouter de musique sauf si le titre est explicitement musical
    is_non_musical_context = is_sport or is_expo or is_cinema or is_conference
    
    if music_detections or concert_detected:
        if is_non_musical_context and not title_has_strong_music:
            # Ne pas ajouter de musique
            pass
        else:
            # Ajouter les categories musique detectees
            for cat in music_detections:
                if cat not in result:
                    result.append(cat)
            
            # Ajouter Concert si detecte et pas de genre specifique
            if concert_detected and not music_detections:
                if 'Musique > Concert' not in result:
                    result.append('Musique > Concert')
    
    # Si "musique" ou "music" est mentionne et aucun genre specifique
    if (_word_in('musique', text) or _word_in('music', text)):
        if not any('Musique' in c for c in result):
            if not is_non_musical_context or title_has_strong_music:
                result.append('Musique > Concert')
    
    # ===========================================================
    # NETTOYAGE FINAL
    # ===========================================================
    
    # Retirer "electro" si c'est "électrique" (guitare, voiture, vélo)
    if 'Musique > Electro' in result:
        if _any_word_in(['électrique', 'électricité', 'énergie'], text):
            if not _any_word_in(['techno', 'dj', 'house', 'rave', 'club'], text):
                result.remove('Musique > Electro')
    
    # Dedupliquage
    result = list(dict.fromkeys(result))
    
    # Fallback si rien
    if not result:
        result = ['Culture']
    
    return result
