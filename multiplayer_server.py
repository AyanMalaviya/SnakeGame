#!/usr/bin/env python3
"""
Multiplayer game server for Linked List Snake
Handles hosting, lobbies, and game state synchronization
"""

import socket
import threading
import json
import time
import uuid
import logging
from dataclasses import dataclass, asdict
from typing import Dict, Optional, Tuple
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GameState(Enum):
    LOBBY = "lobby"
    COUNTDOWN = "countdown"
    PLAYING = "playing"
    GAME_OVER = "game_over"

class PlayerState(Enum):
    WAITING = "waiting"
    READY = "ready"
    PLAYING = "playing"
    DEAD = "dead"

@dataclass
class GameSession:
    session_id: str
    host_id: str
    difficulty: str  # easy, medium, hard
    state: GameState = GameState.LOBBY
    players: Dict[str, 'Player'] = None
    countdown: int = 3
    winner: Optional[str] = None
    created_at: float = None

    def __post_init__(self):
        if self.players is None:
            self.players = {}
        if self.created_at is None:
            self.created_at = time.time()

@dataclass
class Player:
    player_id: str
    session_id: str
    nickname: str
    is_host: bool = False
    state: PlayerState = PlayerState.WAITING
    ready: bool = False
    score: int = 0
    length: int = 1
    connected_at: float = None

    def __post_init__(self):
        if self.connected_at is None:
            self.connected_at = time.time()

class MultiplayerServer:
    def __init__(self, host: str = '0.0.0.0', port: int = 9999):
        self.host = host
        self.port = port
        self.sessions: Dict[str, GameSession] = {}
        self.client_sessions: Dict[str, str] = {}  # client_id -> session_id
        self.server_socket = None
        self.running = False
        self.lock = threading.Lock()

    def start(self):
        """Start the game server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            logger.info(f"Server started on {self.host}:{self.port}")

            while self.running:
                try:
                    client_socket, client_addr = self.server_socket.accept()
                    logger.info(f"Client connected: {client_addr}")
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except Exception as e:
                    logger.error(f"Error accepting connection: {e}")
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop the server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()

    def handle_client(self, client_socket: socket.socket, client_addr: Tuple[str, int]):
        """Handle individual client connections"""
        client_id = str(uuid.uuid4())
        try:
            while self.running:
                try:
                    data = client_socket.recv(4096).decode('utf-8')
                    if not data:
                        break

                    messages = data.split('\n')
                    for message in messages:
                        if message.strip():
                            response = self.process_message(client_id, message.strip())
                            if response:
                                client_socket.send((response + '\n').encode('utf-8'))
                except Exception as e:
                    logger.error(f"Error handling client {client_id}: {e}")
                    break
        finally:
            try:
                # Clean up player session
                with self.lock:
                    if client_id in self.client_sessions:
                        session_id = self.client_sessions[client_id]
                        if session_id in self.sessions:
                            session = self.sessions[session_id]
                            if client_id in session.players:
                                del session.players[client_id]
                        del self.client_sessions[client_id]
                client_socket.close()
                logger.info(f"Client {client_id} disconnected")
            except:
                pass

    def process_message(self, client_id: str, message: str) -> Optional[str]:
        """Process client messages"""
        try:
            data = json.loads(message)
            action = data.get('action')

            if action == 'create_session':
                return self.create_session(client_id, data)
            elif action == 'join_session':
                return self.join_session(client_id, data)
            elif action == 'list_sessions':
                return self.list_sessions()
            elif action == 'set_ready':
                return self.set_ready(client_id, data)
            elif action == 'start_game':
                return self.start_game(client_id)
            elif action == 'game_state':
                return self.update_game_state(client_id, data)
            elif action == 'game_over':
                return self.handle_game_over(client_id, data)
            else:
                return json.dumps({'status': 'error', 'message': 'Unknown action'})
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return json.dumps({'status': 'error', 'message': str(e)})

    def create_session(self, client_id: str, data: dict) -> str:
        """Create a new game session"""
        with self.lock:
            session_id = str(uuid.uuid4())
            difficulty = data.get('difficulty', 'medium')
            nickname = data.get('nickname', 'Host')

            player = Player(
                player_id=client_id,
                session_id=session_id,
                nickname=nickname,
                is_host=True
            )

            session = GameSession(
                session_id=session_id,
                host_id=client_id,
                difficulty=difficulty,
                players={client_id: player}
            )

            self.sessions[session_id] = session
            self.client_sessions[client_id] = session_id

            logger.info(f"Session created: {session_id} by {client_id}")
            return json.dumps({
                'status': 'success',
                'session_id': session_id,
                'message': 'Session created'
            })

    def join_session(self, client_id: str, data: dict) -> str:
        """Join an existing game session"""
        session_id = data.get('session_id')
        nickname = data.get('nickname', 'Player')

        with self.lock:
            if session_id not in self.sessions:
                return json.dumps({'status': 'error', 'message': 'Session not found'})

            session = self.sessions[session_id]

            if session.state != GameState.LOBBY:
                return json.dumps({'status': 'error', 'message': 'Game already started'})

            if len(session.players) >= 2:
                return json.dumps({'status': 'error', 'message': 'Session full'})

            player = Player(
                player_id=client_id,
                session_id=session_id,
                nickname=nickname,
                is_host=False
            )

            session.players[client_id] = player
            self.client_sessions[client_id] = session_id

            logger.info(f"Player {client_id} joined session {session_id}")

            # Notify host
            return json.dumps({
                'status': 'success',
                'session_id': session_id,
                'players': {pid: p.nickname for pid, p in session.players.items()},
                'message': f'{nickname} joined'
            })

    def list_sessions(self) -> str:
        """List available game sessions"""
        with self.lock:
            available = []
            for sid, session in self.sessions.items():
                if session.state == GameState.LOBBY and len(session.players) < 2:
                    available.append({
                        'session_id': sid,
                        'host': session.players[session.host_id].nickname,
                        'difficulty': session.difficulty,
                        'players': len(session.players)
                    })

            return json.dumps({
                'status': 'success',
                'sessions': available
            })

    def set_ready(self, client_id: str, data: dict) -> str:
        """Set player ready state"""
        ready = data.get('ready', False)

        with self.lock:
            if client_id not in self.client_sessions:
                return json.dumps({'status': 'error', 'message': 'Not in a session'})

            session_id = self.client_sessions[client_id]
            session = self.sessions[session_id]
            player = session.players[client_id]

            player.ready = ready
            player.state = PlayerState.READY if ready else PlayerState.WAITING

            # Check if both players are ready
            if len(session.players) == 2:
                all_ready = all(p.ready for p in session.players.values())
                if all_ready:
                    session.state = GameState.COUNTDOWN
                    return json.dumps({
                        'status': 'success',
                        'all_ready': True,
                        'message': 'Both players ready! Starting in 3 seconds'
                    })

            return json.dumps({
                'status': 'success',
                'message': 'Ready state updated'
            })

    def start_game(self, client_id: str) -> str:
        """Start the game (host only)"""
        with self.lock:
            if client_id not in self.client_sessions:
                return json.dumps({'status': 'error', 'message': 'Not in a session'})

            session_id = self.client_sessions[client_id]
            session = self.sessions[session_id]

            if session.host_id != client_id:
                return json.dumps({'status': 'error', 'message': 'Only host can start'})

            if len(session.players) < 2:
                return json.dumps({'status': 'error', 'message': 'Need 2 players'})

            session.state = GameState.PLAYING
            for player in session.players.values():
                player.state = PlayerState.PLAYING

            logger.info(f"Game started in session {session_id}")
            return json.dumps({
                'status': 'success',
                'message': 'Game started'
            })

    def update_game_state(self, client_id: str, data: dict) -> str:
        """Update game state during gameplay"""
        with self.lock:
            if client_id not in self.client_sessions:
                return json.dumps({'status': 'error', 'message': 'Not in a session'})

            session_id = self.client_sessions[client_id]
            session = self.sessions[session_id]
            player = session.players[client_id]

            player.score = data.get('score', 0)
            player.length = data.get('length', 1)

            return json.dumps({'status': 'success'})

    def handle_game_over(self, client_id: str, data: dict) -> str:
        """Handle game over event"""
        with self.lock:
            if client_id not in self.client_sessions:
                return json.dumps({'status': 'error', 'message': 'Not in a session'})

            session_id = self.client_sessions[client_id]
            session = self.sessions[session_id]

            winner_id = data.get('winner_id')
            session.winner = winner_id
            session.state = GameState.GAME_OVER

            logger.info(f"Game over in session {session_id}, winner: {winner_id}")
            return json.dumps({
                'status': 'success',
                'winner': winner_id,
                'message': 'Game over'
            })


if __name__ == '__main__':
    server = MultiplayerServer(port=9999)
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
        server.stop()
