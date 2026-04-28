# Chess Analyzer

A web app that analyzes your Chess.com games using the Stockfish engine.
Enter a username, pick games, and get move-by-move breakdown with blunder
detection, pattern recognition, and best move suggestions.

## Tech Stack

**Backend:** Python, Flask, python-chess, Stockfish  
**Frontend:** Vue 3 (Vite)  
**API:** Chess.com Public API  

## Features

- Fetch games by username, month, and year
- Select specific games, last N games, or full month
- Win%-based move classification (inaccuracy / mistake / blunder)
- Pattern detection (hung pieces, forks, back rank etc.)
- Best move suggestions with optional engine line
- In-session caching so Stockfish doesn't re-run on same games

## Running Locally

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Add your .env (see .env.example)
python app.py
```

## Status

🚧 In development

## License

MIT
