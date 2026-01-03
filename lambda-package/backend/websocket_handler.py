"""
Handler WebSocket pour les notifications et messages en temps réel
"""

import json
import logging
from flask_socketio import SocketIO, emit, join_room, leave_room
from typing import Dict, Optional

logger = logging.getLogger(__name__)

socketio = None

def init_socketio(app):
    """Initialise SocketIO pour l'application Flask"""
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    return socketio

def setup_websocket_handlers(socketio_instance):
    """Configure les handlers WebSocket"""
    global socketio
    socketio = socketio_instance
    
    @socketio.on('connect')
    def handle_connect(auth):
        """Gère la connexion d'un client"""
        user_id = auth.get('userId') if auth else None
        if user_id:
            join_room(f"user_{user_id}")
            logger.info(f"User {user_id} connected")
            emit('connected', {'status': 'ok', 'userId': user_id})
        else:
            emit('error', {'message': 'Authentication required'})
            return False
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Gère la déconnexion d'un client"""
        logger.info("Client disconnected")
    
    @socketio.on('join_group')
    def handle_join_group(data):
        """Rejoindre une room de groupe pour recevoir les messages"""
        group_id = data.get('groupId')
        user_id = data.get('userId')
        
        if group_id and user_id:
            room = f"group_{group_id}"
            join_room(room)
            emit('joined_group', {'groupId': group_id})
            logger.info(f"User {user_id} joined group {group_id}")
    
    @socketio.on('leave_group')
    def handle_leave_group(data):
        """Quitter une room de groupe"""
        group_id = data.get('groupId')
        user_id = data.get('userId')
        
        if group_id:
            room = f"group_{group_id}"
            leave_room(room)
            emit('left_group', {'groupId': group_id})
            logger.info(f"User {user_id} left group {group_id}")
    
    @socketio.on('send_message')
    def handle_send_message(data):
        """Diffuser un nouveau message à tous les membres du groupe"""
        group_id = data.get('groupId')
        message = data.get('message')
        user_id = data.get('userId')
        username = data.get('username')
        
        if group_id and message:
            room = f"group_{group_id}"
            socketio.emit('new_message', {
                'groupId': group_id,
                'userId': user_id,
                'username': username,
                'message': message,
                'timestamp': data.get('timestamp')
            }, room=room)
    
    @socketio.on('send_notification')
    def handle_send_notification(data):
        """Envoyer une notification à un utilisateur spécifique"""
        target_user_id = data.get('targetUserId')
        notification = data.get('notification')
        
        if target_user_id:
            room = f"user_{target_user_id}"
            socketio.emit('notification', notification, room=room)
    
    @socketio.on('message_reaction')
    def handle_message_reaction(data):
        """Diffuser une réaction sur un message"""
        group_id = data.get('groupId')
        message_id = data.get('messageId')
        emoji = data.get('emoji')
        user_id = data.get('userId')
        
        if group_id and message_id:
            room = f"group_{group_id}"
            socketio.emit('reaction_update', {
                'messageId': message_id,
                'emoji': emoji,
                'userId': user_id,
                'action': data.get('action', 'add')  # 'add' or 'remove'
            }, room=room)





