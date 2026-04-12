#!/bin/bash
# Start multiplayer server for Linked List Snake

set -e

echo "======================================"
echo "Linked List Snake - Multiplayer Server"
echo "======================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found"
    exit 1
fi

# Default settings
PORT=${1:-9999}
HOST=${2:-0.0.0.0}

echo "Starting server on $HOST:$PORT..."
echo ""
echo "Server details:"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Local: localhost:$PORT"
echo ""
echo "To join from another computer:"
echo "  - Make sure port $PORT is open in firewall"
echo "  - Use server IP (find with: hostname -I)"
echo "  - Example: 192.168.1.100:$PORT"
echo ""
echo "Press Ctrl+C to stop server"
echo ""

# Run server
python3 -c "
import sys
sys.path.insert(0, '.')
from multiplayer_server import MultiplayerServer

try:
    server = MultiplayerServer(host='$HOST', port=$PORT)
    server.start()
except KeyboardInterrupt:
    print('\n\nServer shutting down...')
    server.stop()
"
