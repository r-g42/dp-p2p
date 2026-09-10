# Differentially Private P2P File Sharing

P2P file-sharing system that compares differential privacy mechanisms for protecting data in transit. Messages and file chunks are encrypted (Fernet/AES) and noise is injected before transmission.

## Files

**Privacy mechanisms** — each implements the same `PeerNode` with a different noise function:
- `laplace.py` — Laplace mechanism (ε-differential privacy)
- `gauss.py` — Gaussian mechanism ((ε,δ)-differential privacy)
- `exp.py` — Exponential mechanism
- `rand.py` — Randomized response

**Infrastructure:**
- `trackerserver.py` — Central tracker server for peer discovery (REGISTER / GET_PEERS)
- `send_messages.py` — Sends test messages to nodes
- `runall.py` — Launches all four mechanism variants and runs test traffic
- `openport.py` — Connectivity check against the tracker

## Running

Start the tracker first, then any mechanism variant:

```bash
python trackerserver.py
python laplace.py        # or gauss.py, exp.py, rand.py
```

Or run all variants at once:

```bash
python runall.py
```

All nodes run on `localhost` by default (tracker on port 8000, peers on 5000–5005).

## Dependencies

```bash
pip install -r requirements.txt
```
