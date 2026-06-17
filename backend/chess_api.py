# chess_api.py
import requests

BASE_URL = "https://api.chess.com/pub/player"

def get_headers(username):
    return {
        "User-Agent": f"ChessAnalyzer/1.0 (user: {username})"
    }
import re

def extract_opening(pgn):
    """Extract opening name from PGN headers."""
    eco_url = re.search(r'\[ECOUrl "([^"]+)"\]', pgn)
    eco = re.search(r'\[ECO "([^"]+)"\]', pgn)
    
    if eco_url:
        slug = eco_url.group(1).split('/')[-1]
        name = slug.replace('-', ' ')
        return name
    elif eco:
        return eco.group(1)
    return None
def fetch_games(username, year, month):
    url = f"{BASE_URL}/{username}/games/{year:04d}/{month:02d}"
    try:
        response = requests.get(url, headers=get_headers(username), timeout=10)
    except requests.exceptions.RequestException as e:
        return None, f"Network error: {str(e)}"

    if response.status_code == 404:
        return None, f"User '{username}' not found or no games in {month}/{year}."
    if response.status_code != 200:
        return None, f"Chess.com API error: {response.status_code}"

    games = response.json().get("games", [])
    return games, None

def parse_game_list(games, username):
    summary = []
    for i, game in enumerate(games):
        white = game["white"]["username"]
        black = game["black"]["username"]

        if white.lower() == username.lower():
            user_color = "white"
            opponent = black
        else:
            user_color = "black"
            opponent = white

        result = game[user_color]["result"]

        summary.append({
            "index": i,
            "opponent": opponent,
            "user_color": user_color,
            "result": result,
            "time_class": game.get("time_class", "unknown"),
            "end_time": game.get("end_time"),
            "pgn": game.get("pgn", ""),
            "opening": extract_opening(game.get("pgn", "")),
        })

    return summary

def select_games(summary, mode, n=None, index=None):
    if mode == "all":
        return summary
    elif mode == "last_n" and n is not None:
        return summary[-n:]
    elif mode == "single" and index is not None:
        match = [g for g in summary if g["index"] == index]
        return match if match else []
    return []