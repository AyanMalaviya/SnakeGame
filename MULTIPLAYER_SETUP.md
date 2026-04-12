# Multiplayer Integration - Quick Setup Guide

## Files Overview

### Original Files (Unchanged)
- `main.py` - Single player game (still works as before)
- Game running: `python3 main.py`

### New Multiplayer Files

#### Server
- `multiplayer_server.py` - Backend server (required for multiplayer)
- `start_multiplayer_server.sh` - Server launcher (Linux/Mac)
- `start_multiplayer_server.bat` - Server launcher (Windows)

#### Client
- `main_multiplayer.py` - **NEW: Start here for multiplayer!**
- `multiplayer_ui.py` - UI screens and menus
- `multiplayer_client.py` - Network client
- `multiplayer_logic.py` - Game collision logic

#### Documentation
- `MULTIPLAYER_GUIDE.md` - Technical reference
- `MULTIPLAYER_QUICKSTART.md` - User quick start
- `MULTIPLAYER_IMPLEMENTATION.md` - Developer guide

---

## 🚀 Quick Start: Play Multiplayer Now

### Step 1: Start the Server

**Linux/macOS:**
```bash
bash start_multiplayer_server.sh
```

**Windows:**
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

✅ Leave this terminal running!

### Step 2: Launch the Game with Multiplayer

**Linux/macOS/Windows:**
```bash
python3 main_multiplayer.py
```

Or if using Windows CMD:
```cmd
python main_multiplayer.py
```

### Step 3: Choose Game Mode

You'll see three options:
1. **SINGLE PLAYER** - Classic game (original main.py)
2. **MULTIPLAYER HOST** - Create a game for others
3. **MULTIPLAYER JOIN** - Join someone's game

### Step 4: For Hosting

1. Select **MULTIPLAYER HOST**
2. Enter your nickname
3. Select difficulty (Easy/Medium/Hard)
4. Press ENTER to create session
5. Wait for another player to join

### Step 5: For Joining

1. Select **MULTIPLAYER JOIN**
2. Enter your nickname
3. System finds available sessions
4. Join the first available session
5. Wait for host to start the game

### Step 6: In-Game

**Controls** (same as single player):
- Arrow Keys or WASD to move
- P to pause
- ESC to quit back to menu

**Winning**:
- Eat more apples than opponent
- Don't let opponent eat your body
- Last snake surviving wins!

---

## 📋 Game Modes Explained

### Single Player
- Classic game against obstacles
- Earn points eating apples
- Reach high scores
- Started from menu option 1

### Multiplayer Host
- You create a session
- Other players join your session
- You select difficulty for everyone
- You start the game when ready
- Best latency (you're the "authority")

### Multiplayer Join
- Browse available games
- Join someone else's session
- Use their selected difficulty
- Wait for host to start

---

## 🎮 Multiplayer Controls

### Menu Navigation
- **Arrow Keys/WASD** - Move selection
- **1/2/3** - Quick select mode
- **ENTER/SPACE** - Confirm
- **ESC** - Back/Exit

### Setup Screen
- **TAB** - Switch between nickname/difficulty
- **Arrow Keys** - Change difficulty
- **Backspace** - Delete nickname character
- **Type** - Enter nickname
- **ENTER** - Continue to game

### In Game
- **Arrow Keys/WASD** - Move snake
- **P** - Pause game
- **ESC** - Quit to menu

### Game Over
- **R** - Ready for rematch
- **C** - Cancel/Back to menu
- **Arrow Keys** - Select option

---

## 🔧 Server Management

### Check If Server Is Running

**Linux/macOS:**
```bash
lsof -i :9999
```

**Windows:**
```cmd
netstat -an | findstr :9999
```

### Stop Server

Press `Ctrl+C` in the server terminal

### Restart Server

```bash
bash start_multiplayer_server.sh
```

---

## 🌐 Network Setup

### Local Network (Same Room)

Works out-of-the-box! Both players on same WiFi/LAN:

```bash
# Computer A (Host runs server)
bash start_multiplayer_server.sh
python3 main_multiplayer.py

# Computer B (Guest, same network)
python3 main_multiplayer.py
# Select Join → Game appears in list
```

### Different Rooms (Same Network)

Server needs to bind to correct interface:

```bash
# Find your IP (Linux/macOS)
hostname -I

# Find your IP (Windows)
ipconfig

# Edit: main_multiplayer.py, line in MultiplayerClient() call
# Change 'localhost' to your_ip_here e.g. '192.168.1.100'
```

### Internet Play (Advanced)

⚠️ Requires router port forwarding (port 9999)

More info in `MULTIPLAYER_GUIDE.md`

---

## 📊 HUD Display

### During Game

**Left Side (Player 1):**
- Player name
- Score
- Snake length

**Right Side (Player 2):**
- Opponent name
- Their score
- Their length

**Center:**
- Vertical divider line

---

## 🏆 Win Conditions

A player **WINS** if:
1. **Opponent eliminated** (ate your body, hit stone, hit wall wrong way)
2. **Longer snake** (if both die same time)
3. **Direct kill** (head hit opponent = instant win)

---

## ⚙️ Difficulty Settings

Each affects:
- Snake speed (SPEED multiplier)
- Number of stones on map
- Score points multiplier

| Mode | Speed | Stones | Score × |
|------|-------|--------|---------|
| Easy | 7 | 4 | 1 |
| Medium | 8 | 12 | 2 |
| Hard | 9 | 22 | 3 |

---

## 🐛 Troubleshooting

### "Cannot connect to server"
- Is server running? Check with `lsof -i :9999`
- Start server: `bash start_multiplayer_server.sh`
- Try again

### "No available sessions"
- No one hosting - create a session yourself
- Host might be full - check session list
- Try refreshing

### "Game won't start"
- Both players ready? Both must click ready
- Server running on correct machine?
- Check firewall isn't blocking port 9999

### "Opponent not visible in game"
- Network lag - wait a moment
- Check connection stable
- Try restarting

### Server connection timeout
- Network issue - check connectivity
- Server might be down - restart it
- Firewall blocking - check rules

---

## 💡 Performance Tips

- **Best experience**: Ethernet > WiFi > Cellular
- **Same network**: Latency < 10ms
- **Avoid lag**: Close other network apps
- **Stable game**: Hard difficulty for slower connections

---

## 🔐 Security Note

**For Local Use Only:**
- No encryption (use on trusted networks)
- No authentication (anyone can join)
- For public internet: Use VPN or tunneling

---

## 📝 Advanced: Custom Setup

### Custom Server Port

Edit in `main_multiplayer.py`, find:
```python
client.connect('localhost', 9999)
```

Change `9999` to your port.

Then start server:
```bash
python3 multiplayer_server.py port_number
```

### Custom Server Host

Edit in `main_multiplayer.py`:
```python
client.connect('your.server.address', 9999)
```

---

## 🎯 What's Next?

Advanced features planned:
- Spectator mode
- Tournament bracket
- Ranked matches
- Leaderboards
- Team mode (2v2)

---

## 📞 Support

Having issues? Check:
1. `MULTIPLAYER_QUICKSTART.md` - User guide
2. `MULTIPLAYER_GUIDE.md` - Technical details
3. Server console for error messages
4. Game console for client errors

---

## 🎮 Enjoy!

You're all set! Launch with:

```bash
python3 main_multiplayer.py
```

Have fun competing! 🐍⚔️🐍

---

**Remember:**
- ✅ Server must be running
- ✅ Both players in same mode (host/join)
- ✅ Same difficulty for fairest match
- ✅ Have fun! 🎉
