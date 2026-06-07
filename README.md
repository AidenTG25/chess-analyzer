# Chess Analyzer

A full-stack web application for analyzing your Chess.com games using the Stockfish engine. Fetch your game history, get move-by-move evaluations, replay positions interactively, and visualize where the game went wrong.

---

## Features

- **Game Fetching** — pulls your recent games from the Chess.com Public API by username, year, and month
- **Deep Move Analysis** — runs every move through the Stockfish UCI engine at configurable depth; classifies each move as Best, Excellent, Good, Inaccuracy, Mistake, or Blunder using win-percentage loss via a sigmoid model
- **Tactical Hints** — flags back-rank threats and uses a custom Static Exchange Evaluation (SEE) algorithm to generate natural-language hints for bad moves
- **Evaluation Graph** — per-move chart showing how the position shifted across the entire game
- **Interactive Board Replay** — step through moves, branch off at any point, and continue playing with Stockfish responding optimally
- **Redis Caching** — analysis results cached for 2 hours (keyed by `username:year:month:game_index`) to avoid redundant engine computation

---

## Project Structure

```
chess-analyzer/
├── backend/
│   ├── app.py          # Flask app + route definitions
│   ├── analyzer.py     # Stockfish integration, move classification, SEE
│   ├── cache.py        # Redis caching layer
│   ├── chess_api.py    # Chess.com API client
│   └── .env.example    # Environment variable template
└── frontend/
    ├── src/
    │   ├── App.vue
    │   └── components/
    │       ├── GameSearch.vue
    │       ├── GameList.vue
    │       ├── ChessBoard.vue
    │       ├── EvalGraph.vue
    │       ├── MoveList.vue
    │       └── AnalysisSummary.vue
    ├── vite.config.js
    └── package.json
```

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- [Stockfish](https://stockfishchess.org/download/) installed and accessible on your system
- Redis running locally (default: `localhost:6379`)

---

## Setup & Running

### 1. Clone the repo

```bash
git clone https://github.com/AidenTG25/chess-blunder-tracker.git
cd chess-blunder-tracker
```

### 2. Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and set STOCKFISH_PATH to your Stockfish binary
```

Your `.env` should look like:

```
STOCKFISH_PATH=C:/path/to/stockfish.exe   # Windows
# STOCKFISH_PATH=/usr/bin/stockfish       # Linux/macOS
REDIS_URL=redis://localhost:6379
```

```bash
# Start the Flask backend (runs on port 5000)
python app.py
```

### 3. Frontend

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start the Vite dev server (runs on port 5173)
npm run dev
```

### 4. Open the app

Navigate to `http://localhost:5173` in your browser.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/games?username=&year=&month=` | Fetch game list from Chess.com |
| `POST` | `/analyze` | Run full Stockfish analysis on a game |
| `POST` | `/bestmove` | Get best move for a given FEN position |

---

## Tech Stack

**Backend:** Python, Flask, python-chess, Stockfish, Redis, Flask-CORS, python-dotenv

**Frontend:** Vue 3, Vite, Axios, cm-chessboard, Chart.js, chess.js

---

## Notes

- Redis is optional — the app works without it, but repeated analysis of the same game will re-run the engine each time
- Chess.com's public API has rate limits on how many games can be fetched per request; this is a platform constraint, not a project one
- The project started as a CLI tool before being rebuilt as a full-stack web app
