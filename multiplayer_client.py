#!/usr/bin/env python3
"""
Multiplayer client for connecting to game server
"""

import socket
import json
import threading
import time
from typing import Optional, Dict, List, Callable
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiplayerClient:
    def __init__(self, server_host: str = 'localhost', server_port: int = 9999):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.connected = False
        self.session_id = None
        self.player_id = None
        self.callbacks: Dict[str, List[Callable]] = {
            'on_player_joined': [],
            'on_game_started': [],
            'on_game_state_update': [],
            'on_game_over': [],
            'on_error': []
        }
        self.receive_thread = None

    def connect(self, server_host: str = None, server_port: int = None) -> bool:
        """Connect to game server"""
        try:
            host = server_host or self.server_host
            port = server_port or self.server_port

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((host, port))
            self.connected = True
            logger.info(f"Connected to server {host}:{port}")

            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()

            return True
        except Exception as e:
            logger.error(f"Failed to connect to server: {e}")
            self.connected = False
            self._trigger_callback('on_error', {'message': f"Connection failed: {e}"})
            return False

    def disconnect(self):
        """Disconnect from server"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass

    def create_session(self, nickname: str, difficulty: str) -> Optional[str]:
        """Create a new multiplayer session"""
        message = {
            'action': 'create_session',
            'nickname': nickname,
            'difficulty': difficulty
        }
        response = self._send_receive(message)
        if response and response.get('status') == 'success':
            self.session_id = response.get('session_id')
            return self.session_id
        return None

    def join_session(self, session_id: str, nickname: str) -> bool:
        """Join an existing multiplayer session"""
        message = {
            'action': 'join_session',
            'session_id': session_id,
            'nickname': nickname
        }
        response = self._send_receive(message)
        if response and response.get('status') == 'success':
            self.session_id = session_id
            self._trigger_callback('on_player_joined', response)
            return True
        else:
            error_msg = response.get('message') if response else 'Unknown error'
            self._trigger_callback('on_error', {'message': error_msg})
            return False

    def list_sessions(self) -> List[Dict]:
        """Get list of available sessions"""
        message = {'action': 'list_sessions'}
        response = self._send_receive(message)
        if response and response.get('status') == 'success':
            return response.get('sessions', [])
        return []

    def set_ready(self, ready: bool) -> bool:
        """Set player ready status"""
        message = {
            'action': 'set_ready',
            'ready': ready
        }
        response = self._send_receive(message)
        if response and response.get('status') == 'success':
            if response.get('all_ready'):
                self._trigger_callback('on_game_started', {})
            return True
        return False

    def start_game(self) -> bool:
        """Start the game (host only)"""
        message = {'action': 'start_game'}
        response = self._send_receive(message)
        if response and response.get('status') == 'success':
            self._trigger_callback('on_game_started', {})
            return True
        else:
            self._trigger_callback('on_error', {'message': response.get('message', 'Failed to start game')})
            return False

    def send_game_state(self, score: int, length: int) -> bool:
        """Send current game state to server"""
        message = {
            'action': 'game_state',
            'score': score,
            'length': length
        }
        response = self._send_receive(message)
        return response and response.get('status') == 'success'

    def send_game_over(self, winner_id: str) -> bool:
        """Send game over event"""
        message = {
            'action': 'game_over',
            'winner_id': winner_id
        }
        response = self._send_receive(message)
        if response and response.get('status') == 'success':
            self._trigger_callback('on_game_over', response)
            return True
        return False

    def add_callback(self, event: str, callback: Callable):
        """Register callback for events"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def _send_receive(self, message: Dict) -> Optional[Dict]:
        """Send message and receive response"""
        try:
            if not self.connected or not self.socket:
                return None

            message_str = json.dumps(message) + '\n'
            self.socket.send(message_str.encode('utf-8'))

            # Simple approach: read response
            response_data = self.socket.recv(4096).decode('utf-8')
            if response_data:
                return json.loads(response_data.strip())
        except Exception as e:
            logger.error(f"Error sending/receiving: {e}")
        return None

    def _receive_messages(self):
        """Receive messages from server"""
        while self.connected:
            try:
                if not self.socket:
                    break
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break
                # Process received messages
            except socket.timeout:
                continue
            except Exception as e:
                logger.error(f"Error receiving: {e}")
                self.connected = False
                break

    def _trigger_callback(self, event: str, data: Dict):
        """Trigger registered callbacks"""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in callback: {e}")
