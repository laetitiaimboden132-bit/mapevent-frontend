# Handler Lambda simple pour tester bcrypt

def lambda_handler(event, context):
    import sys
    import os
    
    result = {
        "statusCode": 200,
        "body": {
            "python_version": sys.version,
            "python_path": sys.path,
            "bcrypt_test": None,
            "error": None
        }
    }
    
    # Tester bcrypt
    try:
        import bcrypt
        result["body"]["bcrypt_test"] = "SUCCESS"
        result["body"]["bcrypt_version"] = getattr(bcrypt, '__version__', 'unknown')
        result["body"]["bcrypt_file"] = getattr(bcrypt, '__file__', 'unknown')
        
        # Test fonctionnel
        password = b"test"
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        result["body"]["bcrypt_hash_test"] = "SUCCESS"
        
    except ImportError as e:
        result["body"]["bcrypt_test"] = "IMPORT_ERROR"
        result["body"]["error"] = str(e)
        result["statusCode"] = 500
        
    except Exception as e:
        result["body"]["bcrypt_test"] = "ERROR"
        result["body"]["error"] = str(e)
        result["statusCode"] = 500
    
    result["body"]["pythonpath"] = os.environ.get('PYTHONPATH', 'not set')
    result["body"]["opt_python_exists"] = os.path.exists('/opt/python')
    
    import json
    return {
        "statusCode": result["statusCode"],
        "body": json.dumps(result["body"], indent=2)
    }
