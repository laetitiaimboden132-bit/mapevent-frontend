# Script de test pour vérifier si bcrypt fonctionne dans Lambda

import sys
import os

print("Python version:", sys.version)
print("Python path:", sys.path)
print("")

# Tester l'import de bcrypt
try:
    import bcrypt
    print("✅ bcrypt importé avec succès")
    print("   Version:", bcrypt.__version__ if hasattr(bcrypt, '__version__') else "inconnue")
    print("   Chemin:", bcrypt.__file__ if hasattr(bcrypt, '__file__') else "inconnu")
    
    # Tester une fonction basique
    password = b"test_password"
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    print("✅ bcrypt fonctionne (hash test réussi)")
    
except ImportError as e:
    print("❌ ERREUR: Impossible d'importer bcrypt")
    print("   Erreur:", str(e))
    print("")
    print("Vérifications:")
    print("   - La layer bcrypt est-elle attachée?")
    print("   - Le chemin Python inclut-il /opt/python?")
    
except Exception as e:
    print("❌ ERREUR lors du test bcrypt")
    print("   Erreur:", str(e))
    import traceback
    traceback.print_exc()

print("")
print("Variables d'environnement PYTHONPATH:", os.environ.get('PYTHONPATH', 'non défini'))
print("Chemin /opt/python existe:", os.path.exists('/opt/python'))
