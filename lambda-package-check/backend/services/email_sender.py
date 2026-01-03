"""
Service d'envoi d'emails traduits pour MapEventAI
Envoie des emails automatiquement traduits dans la langue du destinataire
"""

import os
import logging
from typing import Optional, Dict
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from services.email_translator import translate_text, detect_language_from_email, translate_email_template

logger = logging.getLogger(__name__)

# Configuration SendGrid
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@mapevent.world')
SENDGRID_FROM_NAME = os.getenv('SENDGRID_FROM_NAME', 'MapEvent')

# Templates d'emails (en français, traduits automatiquement)
EMAIL_TEMPLATES = {
    'event_published': {
        'subject': 'Nouvel événement publié sur MapEvent',
        'body': """
Bonjour,

Un nouvel événement a été publié sur MapEvent et pourrait vous intéresser :

📅 {event_title}
📍 {event_location}
📆 {event_date}
🕐 {event_time}

{event_description}

Pour plus d'informations, visitez : {event_url}

Cordialement,
L'équipe MapEvent
        """.strip()
    },
    'event_near_you': {
        'subject': 'Événement près de chez vous',
        'body': """
Bonjour,

Un événement près de chez vous a été publié :

📅 {event_title}
📍 {event_location}
📆 {event_date}
🕐 {event_time}

{event_description}

Découvrez-le sur la carte : {event_url}

Cordialement,
L'équipe MapEvent
        """.strip()
    },
    'booking_published': {
        'subject': 'Nouveau service de booking disponible',
        'body': """
Bonjour,

Un nouveau service de booking a été publié :

🎤 {booking_name}
📍 {booking_location}
🎵 {booking_categories}

{booking_description}

Découvrez-le sur la carte : {booking_url}

Cordialement,
L'équipe MapEvent
        """.strip()
    },
    'service_published': {
        'subject': 'Nouveau service disponible',
        'body': """
Bonjour,

Un nouveau service a été publié :

🔧 {service_name}
📍 {service_location}
📋 {service_categories}

{service_description}

Découvrez-le sur la carte : {service_url}

Cordialement,
L'équipe MapEvent
        """.strip()
    }
}


def send_translated_email(
    to_email: str,
    template_name: str,
    template_vars: Dict[str, str],
    target_language: Optional[str] = None,
    country_code: Optional[str] = None
) -> bool:
    """
    Envoie un email traduit automatiquement dans la langue du destinataire
    
    Args:
        to_email: Email du destinataire
        template_name: Nom du template (event_published, etc.)
        template_vars: Variables à remplacer dans le template
        target_language: Langue cible (détectée automatiquement si None)
        country_code: Code pays pour améliorer la détection
    
    Returns:
        True si l'email a été envoyé avec succès
    """
    try:
        # Détecter la langue si non spécifiée
        if not target_language:
            target_language = detect_language_from_email(to_email, country_code)
        
        # Récupérer le template
        if template_name not in EMAIL_TEMPLATES:
            logger.error(f"Template {template_name} non trouvé")
            return False
        
        template = EMAIL_TEMPLATES[template_name]
        
        # Traduire le template
        translated_template = translate_email_template(template, target_language, source_language='fr')
        
        # Remplacer les variables
        subject = translated_template['subject'].format(**template_vars)
        body = translated_template['body'].format(**template_vars)
        
        # Créer l'email SendGrid
        message = Mail(
            from_email=Email(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
            to_emails=To(to_email),
            subject=subject,
            plain_text_content=Content("text/plain", body)
        )
        
        # Envoyer l'email
        if not SENDGRID_API_KEY:
            logger.error("SENDGRID_API_KEY non configurée")
            return False
        
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        if response.status_code in [200, 201, 202]:
            logger.info(f"Email envoyé avec succès à {to_email} en {target_language}")
            return True
        else:
            logger.error(f"Erreur envoi email: {response.status_code} - {response.body}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi d'email: {e}")
        return False


def send_event_published_email(
    to_email: str,
    event_title: str,
    event_location: str,
    event_date: str,
    event_time: str,
    event_description: str,
    event_url: str,
    country_code: Optional[str] = None
) -> bool:
    """Envoie un email lorsqu'un événement est publié"""
    return send_translated_email(
        to_email=to_email,
        template_name='event_published',
        template_vars={
            'event_title': event_title,
            'event_location': event_location,
            'event_date': event_date,
            'event_time': event_time,
            'event_description': event_description,
            'event_url': event_url
        },
        country_code=country_code
    )


def send_event_near_you_email(
    to_email: str,
    event_title: str,
    event_location: str,
    event_date: str,
    event_time: str,
    event_description: str,
    event_url: str,
    country_code: Optional[str] = None
) -> bool:
    """Envoie un email pour un événement près du destinataire"""
    return send_translated_email(
        to_email=to_email,
        template_name='event_near_you',
        template_vars={
            'event_title': event_title,
            'event_location': event_location,
            'event_date': event_date,
            'event_time': event_time,
            'event_description': event_description,
            'event_url': event_url
        },
        country_code=country_code
    )


