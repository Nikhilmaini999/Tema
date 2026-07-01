# Tema - LAN-Based Music & AI Application

A decentralized music and AI application that operates over Local Area Networks (LAN) without requiring WiFi, cellular data, or internet connectivity. Uses direct data link layer communication with robust transport and presentation layers.

## Architecture Overview

### Network Model
- **Physical Layer**: Ethernet/802.3 direct connection between devices
- **Data Link Layer**: Raw socket communication with custom protocol
- **Transport Layer**: Custom UDP-based protocol with reliability guarantees
- **Application Layer**: Music streaming, AI processing, and metadata exchange

### Key Features
- ✅ Pure LAN operation (no internet required)
- ✅ Peer-to-peer architecture
- ✅ Persistent connections (no session breaks)
- ✅ Standards-compliant security (TLS 1.3 over custom transport)
- ✅ Music streaming and playback
- ✅ Real-time AI processing (music analysis, recommendations)
- ✅ Device discovery and auto-pairing
- ✅ Cross-platform support (Python, Node.js clients)

## Technology Stack

### Backend
- **Python 3.10+** - Core transport layer, AI engine
- **asyncio** - Asynchronous I/O
- **cryptography** - TLS and encryption
- **librosa** - Audio analysis
- **tensorflow/pytorch** - AI model inference

### Frontend
- **React/Vue.js** - Web UI
- **Web Audio API** - Audio playback
- **WebSockets** - Real-time communication to backend

### Protocols
- **Custom Layer 2 Protocol** (TEMA-Protocol-v1)
- **TLS 1.3** for encrypted sessions
- **FLAC/AAC** for audio compression

## Project Structure

```
Tema/
├── backend/
│   ├── transport/          # Custom transport layer
│   ├── ai/                 # AI models & processing
│   ├── music/              # Music streaming engine
│   ├── security/           # Encryption & authentication
│   └── server.py           # Main application server
├── frontend/
│   ├── web/                # React web interface
│   └── mobile/             # Mobile app (React Native)
├── protocol/               # Protocol definitions
├── docs/
│   ├── ARCHITECTURE.md
│   ├── PROTOCOL.md
│   └── SECURITY.md
├── tests/
├── docker/
└── requirements.txt
```

## Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 16+ (for frontend)
- Direct Ethernet connection between devices

### Backend Setup

```bash
# Clone repository
git clone https://github.com/Nikhilmaini999/Tema.git
cd Tema

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run server
python backend/server.py --bind-interface eth0 --port 5353
```

### Frontend Setup

```bash
cd frontend/web
npm install
npm start
```

## Usage

### Start Server Node
```bash
python backend/server.py --mode server
```

### Connect Client Node
```bash
python backend/server.py --mode client --server-mac 00:11:22:33:44:55
```

### Web Interface
Open browser to `http://node-ip:3000`

## Protocol Specification

### TEMA Frame Structure (Layer 2)
```
[Ethernet Header] [TEMA Header] [Payload] [CRC32]
```

- **Destination MAC**: Target device MAC address
- **Source MAC**: Sender MAC address
- **EtherType**: 0x9999 (custom)
- **TEMA Version**: 1
- **Flags**: Encrypted, Compressed, Needs ACK
- **Sequence Number**: 32-bit
- **Payload Type**: Music, AI_Request, Control, etc.

## Security Model

### Authentication
- MAC address whitelisting
- Pre-shared keys for device pairing
- TLS 1.3 certificate pinning

### Encryption
- AES-256-GCM for data encryption
- ChaCha20-Poly1305 alternative
- Per-session ephemeral keys

### Compliance
- ✅ NIST guidelines for cryptography
- ✅ RFC 3394 (AES Key Wrap)
- ✅ RFC 5869 (HKDF - Key Derivation)

## Development

### Run Tests
```bash
pytest tests/ -v
```

### Build Documentation
```bash
cd docs && make html
```

### Docker Support
```bash
docker build -t tema:latest .
docker run --net=host tema:latest
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - See LICENSE file for details

## Roadmap

- [ ] Phase 1: Core transport layer & device discovery
- [ ] Phase 2: Music streaming engine
- [ ] Phase 3: AI model integration
- [ ] Phase 4: Web UI
- [ ] Phase 5: Mobile apps
- [ ] Phase 6: Performance optimization
- [ ] Phase 7: Enterprise deployment

## Support

For issues, questions, or contributions, open an issue or discussion in this repository.

---

**Note**: This application requires direct Ethernet connectivity. WiFi may work with compatible drivers supporting promiscuous mode, but wired connections are recommended for reliability.
