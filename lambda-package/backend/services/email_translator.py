"""
Service de traduction d'emails pour MapEventAI
Traduit automatiquement les emails dans la langue du destinataire
"""

import os
import boto3
import requests
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

# Configuration des providers de traduction
TRANSLATION_PROVIDERS = {
    'aws': {
        'enabled': os.getenv('AWS_TRANSLATE_ENABLED', 'true').lower() == 'true',
        'region': os.getenv('AWS_TRANSLATE_REGION', 'eu-west-1'),
    },
    'google': {
        'enabled': os.getenv('GOOGLE_TRANSLATE_ENABLED', 'false').lower() == 'true',
        'api_key': os.getenv('GOOGLE_TRANSLATE_API_KEY', ''),
    },
    'deepl': {
        'enabled': os.getenv('DEEPL_ENABLED', 'false').lower() == 'true',
        'api_key': os.getenv('DEEPL_API_KEY', ''),
    }
}

# Mapping des langues (code ISO 639-1)
LANGUAGE_CODES = {
    'fr': 'fr',  # Français
    'en': 'en',  # Anglais
    'es': 'es',  # Espagnol
    'de': 'de',  # Allemand
    'it': 'it',  # Italien
    'pt': 'pt',  # Portugais
    'nl': 'nl',  # Néerlandais
    'ru': 'ru',  # Russe
    'ja': 'ja',  # Japonais
    'zh': 'zh',  # Chinois
    'ar': 'ar',  # Arabe
    'hi': 'hi',  # Hindi
    'ko': 'ko',  # Coréen
    'tr': 'tr',  # Turc
    'pl': 'pl',  # Polonais
    'sv': 'sv',  # Suédois
    'da': 'da',  # Danois
    'no': 'no',  # Norvégien
    'fi': 'fi',  # Finnois
    'cs': 'cs',  # Tchèque
    'ro': 'ro',  # Roumain
    'hu': 'hu',  # Hongrois
    'el': 'el',  # Grec
    'th': 'th',  # Thaï
    'vi': 'vi',  # Vietnamien
    'id': 'id',  # Indonésien
    'ms': 'ms',  # Malais
    'he': 'he',  # Hébreu
    'uk': 'uk',  # Ukrainien
    'bg': 'bg',  # Bulgare
    'hr': 'hr',  # Croate
    'sk': 'sk',  # Slovaque
    'sl': 'sl',  # Slovène
    'et': 'et',  # Estonien
    'lv': 'lv',  # Letton
    'lt': 'lt',  # Lituanien
    'mt': 'mt',  # Maltais
    'ga': 'ga',  # Irlandais
    'cy': 'cy',  # Gallois
    'is': 'is',  # Islandais
    'mk': 'mk',  # Macédonien
    'sq': 'sq',  # Albanais
    'sr': 'sr',  # Serbe
    'bs': 'bs',  # Bosniaque
    'me': 'me',  # Monténégrin
    'ca': 'ca',  # Catalan
    'eu': 'eu',  # Basque
    'gl': 'gl',  # Galicien
    'af': 'af',  # Afrikaans
    'sw': 'sw',  # Swahili
    'zu': 'zu',  # Zoulou
    'xh': 'xh',  # Xhosa
    'am': 'am',  # Amharique
    'bn': 'bn',  # Bengali
    'gu': 'gu',  # Gujarati
    'kn': 'kn',  # Kannada
    'ml': 'ml',  # Malayalam
    'mr': 'mr',  # Marathi
    'ne': 'ne',  # Népalais
    'pa': 'pa',  # Pendjabi
    'si': 'si',  # Cingalais
    'ta': 'ta',  # Tamoul
    'te': 'te',  # Télougou
    'ur': 'ur',  # Ourdou
    'fa': 'fa',  # Persan
    'ps': 'ps',  # Pachto
    'uz': 'uz',  # Ouzbek
    'kk': 'kk',  # Kazakh
    'ky': 'ky',  # Kirghiz
    'tg': 'tg',  # Tadjik
    'az': 'az',  # Azéri
    'hy': 'hy',  # Arménien
    'ka': 'ka',  # Géorgien
    'mn': 'mn',  # Mongol
    'my': 'my',  # Birman
    'km': 'km',  # Khmer
    'lo': 'lo',  # Lao
    'ka': 'ka',  # Géorgien
    'be': 'be',  # Biélorusse
    'eo': 'eo',  # Espéranto
    'ia': 'ia',  # Interlingua
    'la': 'la',  # Latin
    'co': 'co',  # Corse
    'gd': 'gd',  # Gaélique écossais
    'br': 'br',  # Breton
    'oc': 'oc',  # Occitan
    'wa': 'wa',  # Wallon
    'li': 'li',  # Limbourgeois
    'fy': 'fy',  # Frison
    'yi': 'yi',  # Yiddish
    'jv': 'jv',  # Javanais
    'su': 'su',  # Soundanais
    'ceb': 'ceb',  # Cebuano
    'haw': 'haw',  # Hawaïen
    'mg': 'mg',  # Malgache
    'sm': 'sm',  # Samoan
    'to': 'to',  # Tongien
    'fj': 'fj',  # Fidjien
    'ty': 'ty',  # Tahitien
    'mi': 'mi',  # Maori
    'wo': 'wo',  # Wolof
    'yo': 'yo',  # Yoruba
    'ig': 'ig',  # Igbo
    'ha': 'ha',  # Haoussa
    'ff': 'ff',  # Peul
    'so': 'so',  # Somali
    'om': 'om',  # Oromo
    'ti': 'ti',  # Tigrigna
    'ak': 'ak',  # Akan
    'rw': 'rw',  # Kinyarwanda
    'rn': 'rn',  # Kirundi
    'ny': 'ny',  # Chichewa
    'sn': 'sn',  # Shona
    'st': 'st',  # Sesotho
    'tn': 'tn',  # Tswana
    've': 've',  # Venda
    'ts': 'ts',  # Tsonga
    'ss': 'ss',  # Swati
    'nr': 'nr',  # Ndébélé du Sud
    'nso': 'nso',  # Sotho du Nord
    'zu': 'zu',  # Zoulou
    'xh': 'xh',  # Xhosa
    'af': 'af',  # Afrikaans
    'nl': 'nl',  # Néerlandais
    'en': 'en',  # Anglais
    'fr': 'fr',  # Français
    'de': 'de',  # Allemand
    'pt': 'pt',  # Portugais
    'es': 'es',  # Espagnol
    'it': 'it',  # Italien
    'ru': 'ru',  # Russe
    'ja': 'ja',  # Japonais
    'zh': 'zh',  # Chinois
    'ar': 'ar',  # Arabe
    'hi': 'hi',  # Hindi
    'ko': 'ko',  # Coréen
    'tr': 'tr',  # Turc
    'pl': 'pl',  # Polonais
    'sv': 'sv',  # Suédois
    'da': 'da',  # Danois
    'no': 'no',  # Norvégien
    'fi': 'fi',  # Finnois
    'cs': 'cs',  # Tchèque
    'ro': 'ro',  # Roumain
    'hu': 'hu',  # Hongrois
    'el': 'el',  # Grec
    'th': 'th',  # Thaï
    'vi': 'vi',  # Vietnamien
    'id': 'id',  # Indonésien
    'ms': 'ms',  # Malais
    'he': 'he',  # Hébreu
    'uk': 'uk',  # Ukrainien
    'bg': 'bg',  # Bulgare
    'hr': 'hr',  # Croate
    'sk': 'sk',  # Slovaque
    'sl': 'sl',  # Slovène
    'et': 'et',  # Estonien
    'lv': 'lv',  # Letton
    'lt': 'lt',  # Lituanien
    'mt': 'mt',  # Maltais
    'ga': 'ga',  # Irlandais
    'cy': 'cy',  # Gallois
    'is': 'is',  # Islandais
    'mk': 'mk',  # Macédonien
    'sq': 'sq',  # Albanais
    'sr': 'sr',  # Serbe
    'bs': 'bs',  # Bosniaque
    'me': 'me',  # Monténégrin
    'ca': 'ca',  # Catalan
    'eu': 'eu',  # Basque
    'gl': 'gl',  # Galicien
    'af': 'af',  # Afrikaans
    'sw': 'sw',  # Swahili
    'zu': 'zu',  # Zoulou
    'xh': 'xh',  # Xhosa
    'am': 'am',  # Amharique
    'bn': 'bn',  # Bengali
    'gu': 'gu',  # Gujarati
    'kn': 'kn',  # Kannada
    'ml': 'ml',  # Malayalam
    'mr': 'mr',  # Marathi
    'ne': 'ne',  # Népalais
    'pa': 'pa',  # Pendjabi
    'si': 'si',  # Cingalais
    'ta': 'ta',  # Tamoul
    'te': 'te',  # Télougou
    'ur': 'ur',  # Ourdou
    'fa': 'fa',  # Persan
    'ps': 'ps',  # Pachto
    'uz': 'uz',  # Ouzbek
    'kk': 'kk',  # Kazakh
    'ky': 'ky',  # Kirghiz
    'tg': 'tg',  # Tadjik
    'az': 'az',  # Azéri
    'hy': 'hy',  # Arménien
    'ka': 'ka',  # Géorgien
    'mn': 'mn',  # Mongol
    'my': 'my',  # Birman
    'km': 'km',  # Khmer
    'lo': 'lo',  # Lao
    'ka': 'ka',  # Géorgien
    'be': 'be',  # Biélorusse
    'eo': 'eo',  # Espéranto
    'ia': 'ia',  # Interlingua
    'la': 'la',  # Latin
    'co': 'co',  # Corse
    'gd': 'gd',  # Gaélique écossais
    'br': 'br',  # Breton
    'oc': 'oc',  # Occitan
    'wa': 'wa',  # Wallon
    'li': 'li',  # Limbourgeois
    'fy': 'fy',  # Frison
    'yi': 'yi',  # Yiddish
    'jv': 'jv',  # Javanais
    'su': 'su',  # Soundanais
    'ceb': 'ceb',  # Cebuano
    'haw': 'haw',  # Hawaïen
    'mg': 'mg',  # Malgache
    'sm': 'sm',  # Samoan
    'to': 'to',  # Tongien
    'fj': 'fj',  # Fidjien
    'ty': 'ty',  # Tahitien
    'mi': 'mi',  # Maori
    'wo': 'wo',  # Wolof
    'yo': 'yo',  # Yoruba
    'ig': 'ig',  # Igbo
    'ha': 'ha',  # Haoussa
    'ff': 'ff',  # Peul
    'so': 'so',  # Somali
    'om': 'om',  # Oromo
    'ti': 'ti',  # Tigrigna
    'ak': 'ak',  # Akan
    'rw': 'rw',  # Kinyarwanda
    'rn': 'rn',  # Kirundi
    'ny': 'ny',  # Chichewa
    'sn': 'sn',  # Shona
    'st': 'st',  # Sesotho
    'tn': 'tn',  # Tswana
    've': 've',  # Venda
    'ts': 'ts',  # Tsonga
    'ss': 'ss',  # Swati
    'nr': 'nr',  # Ndébélé du Sud
    'nso': 'nso',  # Sotho du Nord
}


def detect_language_from_email(email: str, country_code: Optional[str] = None) -> str:
    """
    Détecte la langue probable du destinataire
    Basé sur l'email (domaine) et le code pays
    """
    # Mapping pays → langue
    country_language_map = {
        'FR': 'fr', 'BE': 'fr', 'CH': 'fr', 'CA': 'fr', 'LU': 'fr', 'MC': 'fr',
        'US': 'en', 'GB': 'en', 'IE': 'en', 'AU': 'en', 'NZ': 'en', 'ZA': 'en',
        'ES': 'es', 'MX': 'es', 'AR': 'es', 'CO': 'es', 'CL': 'es', 'PE': 'es',
        'DE': 'de', 'AT': 'de', 'LI': 'de',
        'IT': 'it', 'SM': 'it', 'VA': 'it',
        'PT': 'pt', 'BR': 'pt', 'AO': 'pt', 'MZ': 'pt',
        'NL': 'nl', 'BE': 'nl',
        'RU': 'ru', 'BY': 'ru', 'KZ': 'ru',
        'JP': 'ja',
        'CN': 'zh', 'TW': 'zh', 'HK': 'zh', 'SG': 'zh',
        'SA': 'ar', 'AE': 'ar', 'EG': 'ar', 'MA': 'ar', 'DZ': 'ar', 'IQ': 'ar',
        'IN': 'hi',
        'KR': 'ko',
        'TR': 'tr',
        'PL': 'pl',
        'SE': 'sv',
        'DK': 'da',
        'NO': 'no',
        'FI': 'fi',
        'CZ': 'cs',
        'RO': 'ro',
        'HU': 'hu',
        'GR': 'el',
        'TH': 'th',
        'VN': 'vi',
        'ID': 'id',
        'MY': 'ms',
        'IL': 'he',
        'UA': 'uk',
        'BG': 'bg',
        'HR': 'hr',
        'SK': 'sk',
        'SI': 'sl',
        'EE': 'et',
        'LV': 'lv',
        'LT': 'lt',
        'MT': 'mt',
        'IE': 'ga',
        'GB': 'cy',
        'IS': 'is',
        'MK': 'mk',
        'AL': 'sq',
        'RS': 'sr',
        'BA': 'bs',
        'ME': 'me',
        'AD': 'ca',
        'ES': 'eu',
        'ES': 'gl',
        'ZA': 'af',
        'KE': 'sw', 'TZ': 'sw', 'UG': 'sw',
        'ZA': 'zu', 'ZA': 'xh',
        'ET': 'am',
        'BD': 'bn', 'IN': 'bn',
        'IN': 'gu',
        'IN': 'kn',
        'IN': 'ml',
        'IN': 'mr',
        'NP': 'ne',
        'IN': 'pa', 'PK': 'pa',
        'LK': 'si',
        'IN': 'ta', 'SG': 'ta', 'MY': 'ta',
        'IN': 'te',
        'PK': 'ur', 'IN': 'ur',
        'IR': 'fa', 'AF': 'fa',
        'AF': 'ps',
        'UZ': 'uz',
        'KZ': 'kk',
        'KG': 'ky',
        'TJ': 'tg',
        'AZ': 'az',
        'AM': 'hy',
        'GE': 'ka',
        'MN': 'mn',
        'MM': 'my',
        'KH': 'km',
        'LA': 'lo',
        'BY': 'be',
    }
    
    # Si on a le code pays, l'utiliser
    if country_code and country_code.upper() in country_language_map:
        return country_language_map[country_code.upper()]
    
    # Sinon, essayer de détecter depuis le domaine email
    email_lower = email.lower()
    domain = email_lower.split('@')[1] if '@' in email_lower else ''
    
    # Mapping domaines → langues
    domain_language_map = {
        '.fr': 'fr', '.be': 'fr', '.ch': 'fr', '.ca': 'fr', '.lu': 'fr', '.mc': 'fr',
        '.com': 'en', '.net': 'en', '.org': 'en', '.us': 'en', '.uk': 'en', '.ie': 'en', '.au': 'en', '.nz': 'en',
        '.es': 'es', '.mx': 'es', '.ar': 'es', '.co': 'es', '.cl': 'es', '.pe': 'es',
        '.de': 'de', '.at': 'de',
        '.it': 'it',
        '.pt': 'pt', '.br': 'pt',
        '.nl': 'nl',
        '.ru': 'ru',
        '.jp': 'ja',
        '.cn': 'zh', '.tw': 'zh', '.hk': 'zh', '.sg': 'zh',
        '.sa': 'ar', '.ae': 'ar', '.eg': 'ar', '.ma': 'ar', '.dz': 'ar',
        '.in': 'hi',
        '.kr': 'ko',
        '.tr': 'tr',
        '.pl': 'pl',
        '.se': 'sv',
        '.dk': 'da',
        '.no': 'no',
        '.fi': 'fi',
        '.cz': 'cs',
        '.ro': 'ro',
        '.hu': 'hu',
        '.gr': 'el',
        '.th': 'th',
        '.vn': 'vi',
        '.id': 'id',
        '.my': 'ms',
        '.il': 'he',
        '.ua': 'uk',
        '.bg': 'bg',
        '.hr': 'hr',
        '.sk': 'sk',
        '.si': 'sl',
        '.ee': 'et',
        '.lv': 'lv',
        '.lt': 'lt',
        '.mt': 'mt',
        '.is': 'is',
        '.mk': 'mk',
        '.al': 'sq',
        '.rs': 'sr',
        '.ba': 'bs',
        '.me': 'me',
    }
    
    for domain_ext, lang in domain_language_map.items():
        if domain.endswith(domain_ext):
            return lang
    
    # Par défaut : anglais
    return 'en'


def translate_with_aws(text: str, target_language: str, source_language: str = 'fr') -> Optional[str]:
    """Traduit un texte avec AWS Translate"""
    try:
        translate_client = boto3.client('translate', region_name=TRANSLATION_PROVIDERS['aws']['region'])
        
        result = translate_client.translate_text(
            Text=text,
            SourceLanguageCode=source_language,
            TargetLanguageCode=target_language
        )
        
        return result['TranslatedText']
    except Exception as e:
        logger.error(f"Erreur AWS Translate: {e}")
        return None


def translate_with_google(text: str, target_language: str, source_language: str = 'fr') -> Optional[str]:
    """Traduit un texte avec Google Cloud Translate"""
    try:
        api_key = TRANSLATION_PROVIDERS['google']['api_key']
        if not api_key:
            return None
        
        url = "https://translation.googleapis.com/language/translate/v2"
        params = {
            'key': api_key,
            'q': text,
            'source': source_language,
            'target': target_language,
            'format': 'text'
        }
        
        response = requests.post(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data['data']['translations'][0]['translatedText']
    except Exception as e:
        logger.error(f"Erreur Google Translate: {e}")
        return None


def translate_with_deepl(text: str, target_language: str, source_language: str = 'fr') -> Optional[str]:
    """Traduit un texte avec DeepL"""
    try:
        api_key = TRANSLATION_PROVIDERS['deepl']['api_key']
        if not api_key:
            return None
        
        url = "https://api.deepl.com/v2/translate"
        headers = {
            'Authorization': f'DeepL-Auth-Key {api_key}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'text': text,
            'source_lang': source_language.upper(),
            'target_lang': target_language.upper()
        }
        
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        
        result = response.json()
        return result['translations'][0]['text']
    except Exception as e:
        logger.error(f"Erreur DeepL: {e}")
        return None


def translate_text(text: str, target_language: str, source_language: str = 'fr') -> str:
    """
    Traduit un texte dans la langue cible
    Essaie plusieurs providers avec fallback
    """
    # Si la langue cible est la même que la source, pas de traduction
    if target_language == source_language:
        return text
    
    # Normaliser le code langue
    target_lang = LANGUAGE_CODES.get(target_language.lower(), target_language.lower())
    source_lang = LANGUAGE_CODES.get(source_language.lower(), source_language.lower())
    
    # Essayer AWS Translate d'abord (recommandé)
    if TRANSLATION_PROVIDERS['aws']['enabled']:
        translated = translate_with_aws(text, target_lang, source_lang)
        if translated:
            return translated
    
    # Fallback : Google Translate
    if TRANSLATION_PROVIDERS['google']['enabled']:
        translated = translate_with_google(text, target_lang, source_lang)
        if translated:
            return translated
    
    # Fallback : DeepL (pour langues européennes)
    if TRANSLATION_PROVIDERS['deepl']['enabled'] and target_lang in ['de', 'es', 'it', 'pt', 'nl', 'ru', 'pl', 'ja', 'zh']:
        translated = translate_with_deepl(text, target_lang, source_lang)
        if translated:
            return translated
    
    # Si tout échoue, retourner le texte original
    logger.warning(f"Impossible de traduire en {target_language}, retour du texte original")
    return text


def translate_email_template(template: Dict[str, str], target_language: str, source_language: str = 'fr') -> Dict[str, str]:
    """
    Traduit un template d'email complet
    """
    translated = {}
    for key, value in template.items():
        translated[key] = translate_text(value, target_language, source_language)
    return translated





