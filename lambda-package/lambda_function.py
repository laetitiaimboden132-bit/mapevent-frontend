"""
Point d'entrée Lambda - Importe le handler depuis handler.py
AWS Lambda cherche par défaut lambda_function.lambda_handler
"""

from handler import lambda_handler

# Exporter explicitement pour Lambda
__all__ = ['lambda_handler']


