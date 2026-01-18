"""
Service d'envoi d'emails traduits pour MapEventAI
Envoie des emails automatiquement traduits dans la langue du destinataire
"""

import os
import logging
import json
from typing import Optional, Dict
import requests
# Import lazy de SendGrid pour éviter les problèmes avec cryptography
# Si SendGrid n'est pas disponible, on utilise requests directement
SendGridAPIClient = None
Mail = None
Email = None
To = None
Content = None

# Import lazy de email_translator pour éviter les blocages au démarrage
# from services.email_translator import translate_text, detect_language_from_email, translate_email_template

logger = logging.getLogger(__name__)

# Essayer d'importer SendGrid (peut échouer si cryptography n'est pas disponible)
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_SDK_AVAILABLE = True
    logger.info("SendGrid SDK importé avec succès")
except ImportError as e:
    SENDGRID_SDK_AVAILABLE = False
    logger.warning(f"SendGrid SDK non disponible (cryptography manquante?): {e}. Utilisation de requests directement.")

# Configuration SendGrid
# Nettoyer les espaces (trim) pour éviter les erreurs
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '').strip()
SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@mapevent.world').strip()
SENDGRID_FROM_NAME = os.getenv('SENDGRID_FROM_NAME', 'MapEvent').strip()

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
    },
    'email_verification': {
        'subject': 'Votre code de vérification MapEventAI',
        'body': """
Bonjour {username},

Votre code de vérification MapEventAI est :

🔐 **{code}**

Ce code est valide pendant {expires_in} minutes.

Entrez ce code dans le formulaire de vérification pour confirmer votre adresse email.

Si vous n'avez pas demandé ce code, vous pouvez ignorer cet email.

Cordialement,
L'équipe MapEventAI
        """.strip()
    },
    'email_verification_link': {
        'subject': 'Vérifiez votre adresse email MapEventAI',
        'body': """
Bonjour {username},

Pour finaliser votre inscription sur MapEventAI, veuillez vérifier votre adresse email en cliquant sur le lien ci-dessous :

🔗 **Vérifier mon email**
{verification_url}

Ce lien est valide pendant {expires_in} heures.

Si vous n'avez pas créé de compte, vous pouvez ignorer cet email.

Cordialement,
L'équipe MapEventAI
        """.strip()
    },
    'welcome': {
        'subject': 'Bienvenue sur MapEventAI ! 🎉',
        'body': """
Bonjour {first_name},

Bienvenue sur MapEventAI ! Nous sommes ravis de vous compter parmi nous.

Votre compte a été créé avec succès :
👤 Nom d'utilisateur : {username}
📧 Email : {email}

Vous pouvez maintenant :
- Découvrir des événements près de chez vous
- Publier vos propres événements
- Réserver des services
- Partager vos expériences

Pour commencer, visitez : {app_url}

Si vous avez des questions, n'hésitez pas à nous contacter.

Cordialement,
L'équipe MapEventAI
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
        # Import lazy de email_translator
        try:
            from services.email_translator import translate_text, detect_language_from_email, translate_email_template
        except ImportError as e:
            logger.warning(f"email_translator non disponible: {e}, utilisation du template français")
            # Fallback: pas de traduction
            def detect_language_from_email(email, country_code):
                return 'fr'
            def translate_email_template(template, target_language, source_language='fr'):
                return template
        
        # Détecter la langue si non spécifiée
        if not target_language:
            target_language = detect_language_from_email(to_email, country_code)
        
        # Récupérer le template
        if template_name not in EMAIL_TEMPLATES:
            logger.error(f"Template {template_name} non trouvé")
            return False
        
        template = EMAIL_TEMPLATES[template_name]
        
        # Traduire le template (désactivé temporairement pour debug)
        # translated_template = translate_email_template(template, target_language, source_language='fr')
        translated_template = template  # Utiliser le template original sans traduction
        
        # Remplacer les variables
        try:
            subject = translated_template['subject'].format(**template_vars)
            body = translated_template['body'].format(**template_vars)
        except KeyError as e:
            logger.error(f"Variable manquante dans template_vars: {e}")
            logger.error(f"Variables disponibles: {list(template_vars.keys())}")
            logger.error(f"Template subject: {translated_template['subject']}")
            logger.error(f"Template body: {translated_template['body']}")
            raise
        except Exception as e:
            logger.error(f"Erreur lors du formatage du template: {e}")
            logger.error(f"Template vars: {template_vars}")
            raise
        
        # Envoyer l'email
        if not SENDGRID_API_KEY:
            logger.error("❌ SENDGRID_API_KEY non configurée - Vérifiez les variables d'environnement Lambda")
            logger.error(f"   SENDGRID_API_KEY vide: {not SENDGRID_API_KEY}")
            logger.error(f"   SENDGRID_FROM_EMAIL: {SENDGRID_FROM_EMAIL}")
            logger.error(f"   SENDGRID_FROM_NAME: {SENDGRID_FROM_NAME}")
            return False
        
        logger.info(f"Tentative d'envoi email à {to_email} avec SendGrid")
        logger.info(f"From: {SENDGRID_FROM_EMAIL} ({SENDGRID_FROM_NAME})")
        logger.info(f"Subject: {subject}")
        logger.info(f"Template: {template_name}")
        
        # Utiliser SendGrid SDK si disponible, sinon utiliser l'API REST directement
        if SENDGRID_SDK_AVAILABLE:
            try:
                # Créer l'email SendGrid avec le SDK
                message = Mail(
                    from_email=Email(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
                    to_emails=To(to_email),
                    subject=subject,
                    plain_text_content=Content("text/plain", body)
                )
                sg = SendGridAPIClient(SENDGRID_API_KEY)
                logger.info("SendGridAPIClient créé avec succès")
                response = sg.send(message)
                logger.info(f"SendGrid response status: {response.status_code}")
                logger.info(f"SendGrid response headers: {response.headers}")
                
                if response.status_code in [200, 201, 202]:
                    logger.info(f"✅ Email envoyé avec succès à {to_email} en {target_language}")
                    logger.info(f"✅ SendGrid message ID: {response.headers.get('X-Message-Id', 'N/A')}")
                    return True
                else:
                    logger.error(f"❌ Erreur envoi email: {response.status_code}")
                    logger.error(f"❌ SendGrid response body: {response.body}")
                    logger.error(f"❌ SendGrid response headers: {response.headers}")
                    return False
            except Exception as send_error:
                logger.warning(f"Erreur avec SendGrid SDK: {send_error}. Tentative avec API REST directe...")
                # Fallback vers API REST
                pass
        
        # Fallback: utiliser l'API REST SendGrid directement avec requests
        try:
            url = "https://api.sendgrid.com/v3/mail/send"
            headers = {
                "Authorization": f"Bearer {SENDGRID_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "personalizations": [{
                    "to": [{"email": to_email}],
                    "subject": subject
                }],
                "from": {
                    "email": SENDGRID_FROM_EMAIL,
                    "name": SENDGRID_FROM_NAME
                },
                "content": [{
                    "type": "text/plain",
                    "value": body
                }]
            }
            
            logger.info("Envoi via API REST SendGrid (fallback)")
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            logger.info(f"SendGrid API REST response status: {response.status_code}")
            
            if response.status_code in [200, 201, 202]:
                message_id = response.headers.get('X-Message-Id', 'N/A')
                logger.info(f"✅ Email envoyé avec succès à {to_email} en {target_language} (via API REST)")
                logger.info(f"✅ SendGrid message ID: {message_id}")
                return True
            else:
                logger.error(f"❌ Erreur envoi email via API REST: {response.status_code}")
                logger.error(f"❌ SendGrid response body: {response.text}")
                return False
        except Exception as send_error:
            logger.error(f"❌ Exception lors de l'envoi SendGrid (API REST): {send_error}")
            import traceback
            logger.error(traceback.format_exc())
            raise
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'envoi d'email: {e}")
        import traceback
        logger.error(traceback.format_exc())
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





