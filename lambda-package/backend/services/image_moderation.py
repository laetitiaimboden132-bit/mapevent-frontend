"""
Service de modération d'images pour vérifier l'âge approprié (16+)
Utilise Google Cloud Vision API ou AWS Rekognition
"""

import os
import logging
import requests
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

def moderate_image(image_url: str, user_id: Optional[str] = None) -> Tuple[bool, Dict]:
    """
    Modère une image pour vérifier qu'elle est appropriée (16+)
    
    Returns:
        (is_safe, moderation_result)
        is_safe: True si l'image est appropriée, False sinon
        moderation_result: Détails de la modération
    """
    
    # Essayer Google Cloud Vision API d'abord
    google_api_key = os.getenv('GOOGLE_CLOUD_VISION_API_KEY')
    if google_api_key:
        try:
            return moderate_with_google_vision(image_url, google_api_key)
        except Exception as e:
            logger.warning(f"Google Vision API failed: {e}, trying AWS Rekognition...")
    
    # Fallback sur AWS Rekognition
    aws_region = os.getenv('AWS_REGION', 'eu-central-1')
    try:
        return moderate_with_aws_rekognition(image_url, aws_region)
    except Exception as e:
        logger.error(f"AWS Rekognition failed: {e}")
        # En cas d'échec, on accepte l'image mais on la marque pour révision manuelle
        return (True, {
            'provider': 'none',
            'error': str(e),
            'requires_manual_review': True
        })

def moderate_with_google_vision(image_url: str, api_key: str) -> Tuple[bool, Dict]:
    """Modère avec Google Cloud Vision API"""
    try:
        from google.cloud import vision
        
        client = vision.ImageAnnotatorClient()
        image = vision.Image()
        image.source.image_uri = image_url
        
        # Détecter le contenu inapproprié
        response = client.safe_search_detection(image=image)
        safe = response.safe_search_annotation
        
        # Vérifier les niveaux de risque
        # Les valeurs vont de VERY_UNLIKELY à VERY_LIKELY
        risk_levels = {
            'adult': safe.adult.name,
            'violence': safe.violence.name,
            'racy': safe.racy.name,
            'medical': safe.medical.name,
            'spoof': safe.spoof.name
        }
        
        # Bloquer si ANY risque est LIKELY ou VERY_LIKELY
        is_safe = all(
            level not in ['LIKELY', 'VERY_LIKELY'] 
            for level in risk_levels.values()
        )
        
        return (is_safe, {
            'provider': 'google_vision',
            'risk_levels': risk_levels,
            'is_safe': is_safe
        })
        
    except ImportError:
        # Fallback sur l'API REST si le SDK n'est pas disponible
        return moderate_with_google_vision_rest(image_url, api_key)
    except Exception as e:
        logger.error(f"Google Vision error: {e}")
        raise

def moderate_with_google_vision_rest(image_url: str, api_key: str) -> Tuple[bool, Dict]:
    """Modère avec Google Cloud Vision API via REST"""
    url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
    
    payload = {
        "requests": [{
            "image": {"source": {"imageUri": image_url}},
            "features": [{"type": "SAFE_SEARCH_DETECTION"}]
        }]
    }
    
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    
    result = response.json()
    if 'responses' not in result or not result['responses']:
        raise Exception("Invalid response from Google Vision API")
    
    safe = result['responses'][0].get('safeSearchAnnotation', {})
    
    risk_levels = {
        'adult': safe.get('adult', 'UNKNOWN'),
        'violence': safe.get('violence', 'UNKNOWN'),
        'racy': safe.get('racy', 'UNKNOWN'),
        'medical': safe.get('medical', 'UNKNOWN'),
        'spoof': safe.get('spoof', 'UNKNOWN')
    }
    
    is_safe = all(
        level not in ['LIKELY', 'VERY_LIKELY'] 
        for level in risk_levels.values()
    )
    
    return (is_safe, {
        'provider': 'google_vision_rest',
        'risk_levels': risk_levels,
        'is_safe': is_safe
    })

def moderate_with_aws_rekognition(image_url: str, region: str) -> Tuple[bool, Dict]:
    """Modère avec AWS Rekognition"""
    try:
        import boto3
        
        rekognition = boto3.client('rekognition', region_name=region)
        
        # Télécharger l'image depuis l'URL
        image_response = requests.get(image_url, timeout=10)
        image_response.raise_for_status()
        image_bytes = image_response.content
        
        # Modérer le contenu
        response = rekognition.detect_moderation_labels(
            Image={'Bytes': image_bytes},
            MinConfidence=60.0
        )
        
        moderation_labels = response.get('ModerationLabels', [])
        
        # Bloquer si des labels de contenu inapproprié sont détectés
        inappropriate_labels = [
            'Explicit Nudity',
            'Violence',
            'Visually Disturbing',
            'Rude Gestures',
            'Drugs',
            'Tobacco',
            'Alcohol'
        ]
        
        detected_labels = [label['Name'] for label in moderation_labels]
        has_inappropriate = any(
            label in detected_labels 
            for label in inappropriate_labels
        )
        
        is_safe = not has_inappropriate
        
        return (is_safe, {
            'provider': 'aws_rekognition',
            'detected_labels': detected_labels,
            'moderation_labels': moderation_labels,
            'is_safe': is_safe
        })
        
    except Exception as e:
        logger.error(f"AWS Rekognition error: {e}")
        raise





