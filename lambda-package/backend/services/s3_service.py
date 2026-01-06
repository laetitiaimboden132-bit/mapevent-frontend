"""
Service S3 pour uploader les avatars et images
"""

import boto3
import os
import base64
import logging
import requests
from typing import Optional, Tuple
from io import BytesIO

# Initialiser le logger AVANT de l'utiliser
logger = logging.getLogger(__name__)

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("⚠️ PIL/Pillow non disponible - upload S3 désactivé")

# Configuration S3
S3_BUCKET_NAME = os.getenv('S3_AVATARS_BUCKET', 'mapevent-avatars')
S3_REGION = os.getenv('AWS_REGION', 'eu-west-1')
S3_AVATARS_PREFIX = 'avatars/'

def get_s3_client():
    """Retourne un client S3 configuré"""
    return boto3.client(
        's3',
        region_name=S3_REGION
    )

def download_image_from_url(image_url: str) -> Optional[bytes]:
    """
    Télécharge une image depuis une URL et retourne les données binaires
    
    Args:
        image_url: URL de l'image (ex: https://lh3.googleusercontent.com/...)
    
    Returns:
        Données binaires de l'image ou None en cas d'erreur
    """
    try:
        response = requests.get(image_url, timeout=10, stream=True)
        response.raise_for_status()
        
        # Vérifier le Content-Type
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            logger.warning(f"⚠️ URL ne pointe pas vers une image: {content_type}")
            return None
        
        return response.content
    except Exception as e:
        logger.error(f"❌ Erreur téléchargement image depuis URL: {e}")
        return None

def upload_avatar_to_s3(user_id: str, avatar_input: str) -> Optional[str]:
    """
    Upload un avatar (base64 ou URL) vers S3 et retourne l'URL publique
    
    Args:
        user_id: ID de l'utilisateur
        avatar_input: String base64 de l'image (commence par 'data:image/...') 
                     OU URL de l'image (commence par 'http://' ou 'https://')
    
    Returns:
        URL S3 de l'avatar ou None en cas d'erreur
    """
    try:
        image_data = None
        image_type = 'jpeg'  # Par défaut
        
        # Cas 1: Base64
        if avatar_input.startswith('data:image'):
            # Extraire le type d'image et les données base64
            header, encoded = avatar_input.split(',', 1)
            image_type = header.split('/')[1].split(';')[0]  # Ex: 'jpeg', 'png'
            
            # Décoder base64
            image_data = base64.b64decode(encoded)
        
        # Cas 2: URL (Google, Facebook, etc.)
        elif avatar_input.startswith('http://') or avatar_input.startswith('https://'):
            logger.info(f"📥 Téléchargement avatar depuis URL: {avatar_input}")
            image_data = download_image_from_url(avatar_input)
            if not image_data:
                logger.warning(f"⚠️ Échec téléchargement depuis URL")
                return None
            
            # Détecter le type depuis les données (si PIL disponible)
            if PIL_AVAILABLE:
                try:
                    img = Image.open(BytesIO(image_data))
                    image_type = img.format.lower() if img.format else 'jpeg'
                except Exception:
                    # Par défaut JPEG si on ne peut pas détecter
                    image_type = 'jpeg'
            else:
                # PIL non disponible - utiliser JPEG par défaut
                image_type = 'jpeg'
        
        else:
            logger.warning(f"⚠️ Format avatar non supporté: {avatar_input[:50]}...")
            return None
        
        # Optimiser l'image si nécessaire (réduire la taille) - seulement si PIL disponible
        if PIL_AVAILABLE:
            try:
                img = Image.open(BytesIO(image_data))
                # Convertir en RGB si nécessaire (pour JPEG)
                if image_type.lower() in ['jpeg', 'jpg'] and img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Redimensionner si trop grand (max 800x800 pour les avatars)
                max_size = 800
                if img.width > max_size or img.height > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # Sauvegarder dans un buffer
                output = BytesIO()
                format_to_use = 'JPEG' if image_type.lower() in ['jpeg', 'jpg'] else 'PNG'
                img.save(output, format=format_to_use, quality=85, optimize=True)
                image_data = output.getvalue()
                image_type = 'jpeg' if format_to_use == 'JPEG' else 'png'
            except Exception as img_error:
                logger.warning(f"⚠️ Erreur optimisation image: {img_error}, utilisation image originale")
        else:
            # PIL non disponible - upload direct sans optimisation
            # Limiter la taille si trop grande (max 5MB pour éviter les problèmes)
            max_size_bytes = 5 * 1024 * 1024  # 5MB
            if len(image_data) > max_size_bytes:
                logger.warning(f"⚠️ Image trop volumineuse ({len(image_data)} bytes > {max_size_bytes} bytes) - troncature")
                # Tronquer les données (dernier recours)
                image_data = image_data[:max_size_bytes]
            logger.info("ℹ️ PIL non disponible - upload image originale sans optimisation")
        
        # Générer la clé S3
        file_extension = 'jpg' if image_type.lower() in ['jpeg', 'jpg'] else image_type.lower()
        s3_key = f"{S3_AVATARS_PREFIX}{user_id}.{file_extension}"
        
        # Upload vers S3
        s3_client = get_s3_client()
        # Note: ACL retiré car le bucket n'autorise pas les ACLs
        # La visibilité publique doit être gérée via la politique du bucket
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=image_data,
            ContentType=f'image/{image_type}',
            CacheControl='max-age=31536000'  # Cache 1 an
        )
        
        # Générer l'URL publique
        # Format: https://bucket-name.s3.region.amazonaws.com/key
        avatar_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
        
        logger.info(f"✅ Avatar uploadé vers S3: {avatar_url} ({len(image_data)} bytes)")
        return avatar_url
        
    except Exception as e:
        logger.error(f"❌ Erreur upload avatar vers S3: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def delete_avatar_from_s3(user_id: str) -> bool:
    """
    Supprime l'avatar d'un utilisateur de S3
    
    Args:
        user_id: ID de l'utilisateur
    
    Returns:
        True si succès, False sinon
    """
    try:
        s3_client = get_s3_client()
        
        # Essayer de supprimer les différents formats possibles
        extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        deleted = False
        
        for ext in extensions:
            s3_key = f"{S3_AVATARS_PREFIX}{user_id}.{ext}"
            try:
                s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
                deleted = True
                logger.info(f"✅ Avatar supprimé de S3: {s3_key}")
            except Exception as e:
                # Ignorer si le fichier n'existe pas
                pass
        
        return deleted
        
    except Exception as e:
        logger.error(f"❌ Erreur suppression avatar de S3: {e}")
        return False

