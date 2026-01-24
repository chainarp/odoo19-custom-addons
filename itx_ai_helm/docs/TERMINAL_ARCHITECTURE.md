# Terminal Architecture

## Overview

ITX AI Helm Terminal ใช้ **Bus.bus (Primary) + Long Polling (Fallback)** สำหรับ real-time terminal communication ใน Odoo 19.

## Connection Strategy

```
┌─────────────────────────────────────────────────────────┐
│           Bus.bus (Primary) + Polling (Fallback)        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Output: bus.bus._sendone() ──▶ bus_service.subscribe() │
│          (Real-time push via Odoo WebSocket)            │
│                                                         │
│  Input:  JSON-RPC POST ──▶ /terminal/write              │
│          (Standard Odoo RPC with batching)              │
│                                                         │
│  Fallback: Long Polling /terminal/poll (if bus fails)   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Components

### Backend (Python)

| File | Description |
|------|-------------|
| `services/terminal_manager.py` | PTY process management, output broadcasting |
| `services/bus_broadcaster.py` | Thread-safe Bus.bus broadcaster with batching |
| `controllers/terminal_websocket.py` | JSON-RPC endpoints for connect/write/resize/poll |
| `models/terminal_session.py` | Database model for session persistence |

### Frontend (JavaScript)

| File | Description |
|------|-------------|
| `services/terminal_connection.js` | Connection manager (Bus/Polling modes) |
| `components/terminal/terminal.js` | OWL component with xterm.js |
| `components/terminal/terminal.xml` | QWeb template |
| `components/terminal/terminal.scss` | Styles |

## Data Flow

### Input (Client → Server)

```
User keystroke
    │
    ▼
TerminalConnectionManager.sendInput()
    │
    ├── Special key (Enter, Ctrl+C, Arrow)? ──▶ Send immediately
    │
    └── Regular character ──▶ Buffer (5ms) ──▶ Batch send
                                                   │
                                                   ▼
                                        JSON-RPC /terminal/write
                                                   │
                                                   ▼
                                        TerminalSession.write()
                                                   │
                                                   ▼
                                           PTY (os.write)
```

### Output (Server → Client)

#### Bus Mode (Primary)

```
PTY output (os.read)
    │
    ▼
TerminalSession._read_output()
    │
    ├── Add to output_buffer (history)
    ├── Add to pending_output (polling fallback)
    │
    └── _broadcast_to_bus()
            │
            ▼
    BusBroadcaster.broadcast()
            │
            ▼
    Buffer (50ms batching)
            │
            ▼
    bus.bus._sendone()
            │
            ▼
    Odoo WebSocket
            │
            ▼
    bus_service.subscribe()
            │
            ▼
    terminal.write()
```

#### Polling Mode (Fallback)

```
Client
    │
    ▼
Poll /terminal/poll (timeout=30s)
    │
    ▼
session.get_pending_output()
    │
    ▼
Return output (clear pending)
    │
    ▼
terminal.write()
    │
    ▼
Poll again immediately
```

## Optimizations

### Input Batching

- Regular characters: Buffer for 5ms, then send together
- Special keys (Enter, Ctrl+C, Escape, Arrow): Send immediately
- Reduces HTTP overhead from N requests to 1 request

### Output Batching (Bus Broadcaster)

- Buffer output for 50ms
- Batch all sessions in single DB transaction
- Max 20 broadcasts/second per session
- Non-blocking: doesn't block PTY reader thread

## Connection Modes

| Mode | Output | Latency | Scalability |
|------|--------|---------|-------------|
| **Bus** | Real-time push | ~50ms | Excellent (WebSocket) |
| **Polling** | Poll every 0.1s | ~100ms | Poor (holds workers) |

## API Endpoints

| Endpoint | Type | Description |
|----------|------|-------------|
| `/terminal/connect` | JSON-RPC | Create/resume session |
| `/terminal/write` | JSON-RPC | Send input to terminal |
| `/terminal/resize` | JSON-RPC | Resize terminal (rows, cols) |
| `/terminal/poll` | JSON-RPC | Get output (polling mode) |
| `/terminal/disconnect` | JSON-RPC | Close session |

## Session Resume

Sessions persist across page refreshes:

1. Session ID stored in `localStorage`
2. On reconnect, tries to resume existing session
3. If session dead, creates new one
4. History (500 lines) sent on resume

## Bus Channel Naming

```
Channel: terminal_{session_id}
Message Type: terminal_output
Payload: { session_id, output }
```
