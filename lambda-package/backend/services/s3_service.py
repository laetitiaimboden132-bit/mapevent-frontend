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
from datetime import timedelta

# Initialiser le logger AVANT de l'utiliser
logger = logging.getLogger(__name__)

try:
    from PIL import Image
    PIL_AVAILABLE = True
    logger.info("✅ PIL/Pillow disponible")
except ImportError as e:
    PIL_AVAILABLE = False
    logger.warning(f"⚠️ PIL/Pillow non disponible: {e} - upload S3 fonctionnera sans optimisation")

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
        # Suivre les redirections et utiliser un User-Agent pour éviter les blocages
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(image_url, timeout=15, stream=True, headers=headers, allow_redirects=True)
        response.raise_for_status()
        
        # Vérifier le Content-Type
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            logger.warning(f"⚠️ URL ne pointe pas vers une image: {content_type}, URL: {image_url[:100]}")
            # Essayer quand même si c'est une URL Google (parfois le Content-Type est manquant)
            if 'googleusercontent.com' in image_url:
                logger.info("ℹ️ URL Google détectée, téléchargement quand même")
            else:
                return None
        
        # Télécharger tout le contenu
        image_data = response.content
        logger.info(f"📥 Image téléchargée: {len(image_data)} bytes, Content-Type: {content_type}, URL finale: {response.url[:100]}")
        
        # Vérifier que l'image n'est pas trop petite (probablement corrompue ou placeholder)
        # Pour les images PNG/JPEG valides, la taille minimale est généralement > 500 bytes
        if len(image_data) < 500:
            logger.warning(f"⚠️ Image très petite ({len(image_data)} bytes), possiblement corrompue ou placeholder")
            # Pour les URLs Google, essayer sans le paramètre de taille
            if 'googleusercontent.com' in image_url and '=s' in image_url:
                logger.info(f"🔄 Tentative avec URL Google sans paramètre de taille...")
                # Essayer l'URL de base sans paramètres
                base_url = image_url.split('=')[0]
                try:
                    retry_response = requests.get(base_url, timeout=15, stream=True, headers=headers, allow_redirects=True)
                    retry_response.raise_for_status()
                    retry_data = retry_response.content
                    if len(retry_data) > len(image_data):
                        logger.info(f"✅ Image retry plus grande: {len(retry_data)} bytes")
                        return retry_data
                except Exception as retry_error:
                    logger.warning(f"⚠️ Retry échoué: {retry_error}")
            return None
        
        return image_data
    except Exception as e:
        logger.error(f"❌ Erreur téléchargement image depuis URL: {e}")
        import traceback
        logger.error(traceback.format_exc())
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
            mime_type = header.split('/')[1].split(';')[0]  # Ex: 'jpeg', 'png'
            
            # VALIDATION: Vérifier le type MIME autorisé
            allowed_types = ['jpeg', 'jpg', 'png', 'gif', 'webp']
            if mime_type.lower() not in allowed_types:
                logger.error(f"❌ Type d'image non autorisé: {mime_type}")
                return None
            
            image_type = mime_type
            
            # Décoder base64
            image_data = base64.b64decode(encoded)
            
            # VALIDATION: Vérifier la taille (max 5MB)
            max_size_bytes = 5 * 1024 * 1024  # 5MB
            if len(image_data) > max_size_bytes:
                logger.error(f"❌ Image trop volumineuse: {len(image_data)} bytes > {max_size_bytes} bytes")
                return None
        
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
        
        # VALIDATION: Vérifier que c'est bien une image valide
        if PIL_AVAILABLE:
            try:
                img = Image.open(BytesIO(image_data))
                
                # VALIDATION: Vérifier les dimensions (max 2000x2000px)
                max_dimension = 2000
                if img.width > max_dimension or img.height > max_dimension:
                    logger.warning(f"⚠️ Image trop grande: {img.width}x{img.height}, redimensionnement...")
                    # Redimensionner proportionnellement
                    ratio = min(max_dimension / img.width, max_dimension / img.height)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
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
                logger.error(f"❌ Erreur validation/optimisation image: {img_error}")
                return None  # Rejeter l'image si elle ne peut pas être validée
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
        
        # Upload vers S3 (PRIVÉ - pas d'accès public direct)
        s3_client = get_s3_client()
        # IMPORTANT: Ne pas rendre l'objet public. Utiliser des URLs signées à la place.
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=image_data,
            ContentType=f'image/{image_type}',
            CacheControl='max-age=31536000',  # Cache 1 an
            ServerSideEncryption='AES256'  # Chiffrement côté serveur
        )
        
        # Générer une URL signée (presigned URL) valide 1 heure
        # Les URLs signées permettent un accès temporaire sans rendre l'objet public
        avatar_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=3600  # 1 heure
        )
        
        logger.info(f"✅ Avatar uploadé vers S3 avec URL signée: {s3_key} ({len(image_data)} bytes)")
        return avatar_url
        
    except Exception as e:
        logger.error(f"❌ Erreur upload avatar vers S3: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def get_presigned_avatar_url(user_id: str, expiration: int = 3600) -> Optional[str]:
    """
    Génère une URL signée pour accéder à l'avatar d'un utilisateur.
    
    Args:
        user_id: ID de l'utilisateur
        expiration: Durée de validité en secondes (défaut: 1 heure)
    
    Returns:
        URL signée ou None si l'avatar n'existe pas
    """
    try:
        s3_client = get_s3_client()
        
        # Essayer les différents formats possibles
        extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        
        for ext in extensions:
            s3_key = f"{S3_AVATARS_PREFIX}{user_id}.{ext}"
            try:
                # Vérifier si l'objet existe
                s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
                
                # Générer l'URL signée
                url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': S3_BUCKET_NAME, 'Key': s3_key},
                    ExpiresIn=expiration
                )
                logger.info(f"✅ URL signée générée pour {s3_key}")
                return url
            except Exception:
                # Objet n'existe pas dans ce format, essayer le suivant
                continue
        
        # Aucun avatar trouvé
        logger.warning(f"⚠️ Aucun avatar trouvé pour user_id: {user_id}")
        return None
        
    except Exception as e:
        logger.error(f"❌ Erreur génération URL signée: {e}")
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

