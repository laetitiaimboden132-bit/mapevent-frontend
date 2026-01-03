"""
Script de test pour la modération d'images
"""

import sys
from pathlib import Path

# Ajouter le chemin du backend
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from services.image_moderation import moderate_image

def test_image_moderation():
    """Test la modération d'images avec différentes URLs"""
    
    # URLs de test (images publiques appropriées)
    test_images = [
        {
            'url': 'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7',
            'description': 'Voiture (devrait être safe)',
            'expected_safe': True
        },
        {
            'url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4',
            'description': 'Paysage (devrait être safe)',
            'expected_safe': True
        },
        {
            'url': 'https://images.unsplash.com/photo-1519681393784-d120267933ba',
            'description': 'Montagne (devrait être safe)',
            'expected_safe': True
        }
    ]
    
    print("🧪 Test de modération d'images\n")
    print("=" * 60)
    
    for i, test in enumerate(test_images, 1):
        print(f"\n📸 Test {i}: {test['description']}")
        print(f"   URL: {test['url']}")
        
        try:
            is_safe, result = moderate_image(test['url'])
            
            print(f"   ✅ Résultat: {'SAFE' if is_safe else 'UNSAFE'}")
            print(f"   📊 Provider: {result.get('provider', 'unknown')}")
            
            if 'risk_levels' in result:
                print(f"   🔍 Niveaux de risque:")
                for level, value in result['risk_levels'].items():
                    print(f"      - {level}: {value}")
            
            if 'detected_labels' in result:
                print(f"   🏷️  Labels détectés: {', '.join(result['detected_labels'][:5])}")
            
            if is_safe == test['expected_safe']:
                print(f"   ✅ Test réussi!")
            else:
                print(f"   ⚠️  Test échoué (attendu: {test['expected_safe']}, obtenu: {is_safe})")
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            print(f"   ℹ️  Note: Vérifiez que les clés API sont configurées")
    
    print("\n" + "=" * 60)
    print("\n✅ Tests terminés!")
    print("\n💡 Note: Pour tester avec de vraies images:")
    print("   1. Configurez GOOGLE_CLOUD_VISION_API_KEY ou AWS_REGION")
    print("   2. Utilisez des URLs d'images réelles")
    print("   3. Vérifiez les résultats dans la console")

if __name__ == '__main__':
    test_image_moderation()





