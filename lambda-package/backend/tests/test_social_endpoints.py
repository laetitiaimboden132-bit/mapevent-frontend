"""
Tests unitaires pour les endpoints sociaux
"""

import unittest
import json
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Ajouter le chemin du backend
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from main import create_app

class TestSocialEndpoints(unittest.TestCase):
    """Tests pour les endpoints sociaux"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
    
    @patch('main.get_db_connection')
    def test_send_friend_request(self, mock_db):
        """Test envoi de demande d'ami"""
        # Mock de la connexion DB
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # Pas de demande existante
        mock_conn.cursor.return_value = mock_cursor
        mock_db.return_value = mock_conn
        
        response = self.client.post('/api/social/friends/request', 
            json={'userId': 'user1', 'friendId': 'user2'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))
    
    @patch('main.get_db_connection')
    def test_create_group(self, mock_db):
        """Test création de groupe"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db.return_value = mock_conn
        
        response = self.client.post('/api/social/groups',
            json={
                'name': 'Test Group',
                'description': 'Description test',
                'type': 'public',
                'creatorId': 'user1',
                'icon': '👥'
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))
        self.assertIn('groupId', data)
    
    @patch('main.get_db_connection')
    def test_send_group_message(self, mock_db):
        """Test envoi de message dans un groupe"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ('member',)  # Utilisateur est membre
        mock_cursor.fetchone.side_effect = [('member',), (1, '2024-01-01')]  # Deux appels
        mock_conn.cursor.return_value = mock_cursor
        mock_db.return_value = mock_conn
        
        response = self.client.post('/api/social/groups/group123/messages',
            json={
                'userId': 'user1',
                'message': 'Hello world!',
                'attachments': []
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))
        self.assertIn('messageId', data)
    
    @patch('services.image_moderation.moderate_image')
    def test_moderate_image_endpoint(self, mock_moderate):
        """Test modération d'image"""
        mock_moderate.return_value = (True, {'provider': 'test', 'is_safe': True})
        
        with patch('main.get_db_connection') as mock_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_db.return_value = mock_conn
            
            response = self.client.post('/api/social/moderation/image',
                json={
                    'imageUrl': 'https://example.com/image.jpg',
                    'userId': 'user1'
                },
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data.get('isSafe'))
    
    @patch('main.get_db_connection')
    def test_add_message_reaction(self, mock_db):
        """Test ajout de réaction à un message"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ('{}',)  # Pas de réactions existantes
        mock_conn.cursor.return_value = mock_cursor
        mock_db.return_value = mock_conn
        
        response = self.client.post('/api/social/messages/msg123/reaction',
            json={
                'userId': 'user1',
                'emoji': '👍'
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))
        self.assertIn('reactions', data)

if __name__ == '__main__':
    unittest.main()





