# Quick Start: Multiplayer Mode

## 1. Start the Server

### Linux/macOS
```bash
bash start_multiplayer_server.sh
```

### Windows
```cmd
start_multiplayer_server.bat
```

**Output should show:**
```
======================================
Linked List Snake - Multiplayer Server
======================================

Starting server on 0.0.0.0:9999...
```

Leave this running - it's the game server!

## 2. Launch the Game

In a new terminal:

```bash
python3 main.py
```

Or on Windows:
```cmd
python main.py
```

## 3. Host a Game

1. Select **"Multiplayer (Host)"** from the menu
2. Enter your nickname
3. Select difficulty (Easy/Medium/Hard)
4. Wait for another player to join (see "Waiting for Players" screen)

## 4. Join a Game

1. Select **"Multiplayer (Join)"** from the menu
2. View available sessions
3. Click "Join" on the session you want
4. Enter your nickname
5. Wait for host to start the game

## 5. In-Game

**Controls:** Same as single player
- Arrow Keys or WASD to move
- Eat apples while avoiding opponent
- Try to make opponent hit your body or a stone

**Winning Conditions:**
- Opponent runs into you or a stone
- Longer snake wins if both die
- First to kill opponent wins

## 6. After Game

- **Rematch**: Both click "Ready" to play again
- **Menu**: Click "Cancel" to return to main menu

---

## Playing Over Network

### Same Computer (2 Players, 1 Computer)
- Works as described above!

### Local Network (2 Computers)

**Computer 1 (Host):**
```bash
bash start_multiplayer_server.sh
```

**Computer 2:**
```bash
# Edit main.py, find MultiplayerClient, set:
# server_host = "192.168.1.100"  (Computer 1's IP)
python3 main.py
```

**Find Computer 1's IP:**
- Linux/macOS: `hostname -I`
- Windows: `ipconfig` (look for IPv4 Address)

### Internet Play

⚠️ Requires additional setup:
- Port forwarding on router (port 9999)
- Firewall rules to allow connections
- Host's public IP address
- Network latency may affect gameplay

---

## Troubleshooting

### "Connection refused"
- Server not running? Start it with `start_multiplayer_server.sh`
- Server on different computer? Update server IP in code
- Firewall blocking? Check firewall settings

### "Session not found"
- Session already full (2 players max)
- Session ended automatically
- Try refreshing the session list

### "No sessions available"
- No one has created a session yet
- All sessions are full
- Create your own session to host

### Game starts but no opponent visible
- Your opponent is loading
- Network lag - wait a moment
- Restart both clients

### Server crashes
- Check console for error messages
- Restart server: `bash start_multiplayer_server.sh`
- Check firewall isn't blocking port 9999

---

## Advanced: Custom Network Setup

### Custom Port

**Start server:**
```bash
bash start_multiplayer_server.sh 8888  # Use port 8888
```

**Connect from client:**
```python
# In main.py
from multiplayer_client import MultiplayerClient
client = MultiplayerClient(server_port=8888)
```

### Custom Host

**Start server on specific IP:**
```bash
bash start_multiplayer_server.sh 9999 192.168.1.100
```

### Remote Server

**For cloud-hosted server:**
```python
client = MultiplayerClient(
    server_host="your-server.com",
    server_port=9999
)
```

---

## Performance Tips

- **Smooth gameplay**: Use hardwired connection (Ethernet best)
- **Reduce latency**: Game on same network as server
- **Server load**: 1 server can handle 100+ concurrent sessions
- **Bandwidth**: ~10KB/sec per active game

---

## Tips & Tricks

### Strategy
- Position body to trap opponent
- Stones are your friend - force opponent into them
- Control middle of map = more room to maneuver
- Let opponent eat your older segments (less dangerous)

### Advanced
- Predict opponent's moves (they same difficulty levels)
- Build "walls" with your body
- Use map wrapping (portals) to escape

### For Boring Games
- Choose hard difficulty for faster action
- Play on smaller maps Edit `COLS` and `ROWS` in code)
- Add more stones (edit code)

---

## Multiplayer Strategy Guide

### Defense
1. Create walls with your body
2. Force opponent into cramped areas
3. Use stones strategically

### Offense
1. Find gaps in opponent's body
2. Attack from the side (safer)
3. Control center of map

### Apple Strategy
1. Race for apples early (growth = advantage)
2. Predict apple spawns
3. Balance eating with avoiding opponent

---

## Bugs & Feedback

Found a bug? Check:
1. Both clients on same version
2. Server running and responding
3. Network connection stable
4. Console for error messages

Submit issues on GitHub! 🐛

---

Happy snake hunting! 🎮🐍
