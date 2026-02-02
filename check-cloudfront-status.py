#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vérifier le statut de propagation CloudFront"""

import boto3
import time
import sys

DISTRIBUTION_ID = "EMB53HDL7VFIJ"

def check_cloudfront_status():
    cloudfront = boto3.client('cloudfront', region_name='us-east-1')
    
    print("="*60)
    print("VERIFICATION STATUT CLOUDFRONT")
    print("="*60)
    print(f"Distribution ID: {DISTRIBUTION_ID}")
    print()
    
    max_attempts = 30  # 30 tentatives = 15 minutes max
    attempt = 0
    
    while attempt < max_attempts:
        try:
            dist = cloudfront.get_distribution(Id=DISTRIBUTION_ID)
            status = dist['Distribution']['Status']
            last_modified = dist['Distribution']['LastModifiedTime']
            
            print(f"[{attempt + 1}/{max_attempts}] Status: {status}", end="")
            
            if status == 'Deployed':
                print(" ✅")
                print()
                print("="*60)
                print("✅ PROPAGATION TERMINEE!")
                print("="*60)
                print(f"Distribution: {dist['Distribution']['DomainName']}")
                print(f"Derniere modification: {last_modified}")
                print()
                print("Le lien /verify-email devrait maintenant fonctionner!")
                print("Vous pouvez tester le lien de verification email.")
                return True
            elif status == 'InProgress':
                print(" ⏳")
                time.sleep(30)  # Attendre 30 secondes
            else:
                print(f" (Status inattendu: {status})")
                time.sleep(30)
            
            attempt += 1
            
        except Exception as e:
            print(f"\nErreur: {e}")
            time.sleep(30)
            attempt += 1
    
    print()
    print("="*60)
    print("⏳ PROPAGATION EN COURS")
    print("="*60)
    print("La propagation prend generalement 5-15 minutes.")
    print("Vous pouvez relancer ce script plus tard pour verifier.")
    return False

if __name__ == '__main__':
    success = check_cloudfront_status()
    sys.exit(0 if success else 1)
