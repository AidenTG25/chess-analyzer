# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import cache
from chess_api import fetch_games, parse_game_list, select_games
from analyzer import analyze_game

app = Flask(__name__)
CORS(app)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/games", methods=["POST"])
def games():
    data = request.get_json()

    username = data.get("username", "").strip().lower()
    year = data.get("year")
    month = data.get("month")

    if not username or not year or not month:
        return jsonify({"error": "username, year, and month are required"}), 400

    cache_key = f"games:{username}:{year}:{month}"
    cached = cache.get(cache_key)
    if cached:
        return jsonify({"games": cached, "cached": True})

    raw_games, err = fetch_games(username, year, month)
    if err:
        return jsonify({"error": err}), 404
    if not raw_games:
        return jsonify({"games": [], "cached": False})

    summary = parse_game_list(raw_games, username)

    cache.set(cache_key, summary)

    return jsonify({"games": summary, "cached": False})


@app.route("/bestmove", methods=["POST"])
def bestmove():
    data = request.get_json()
    fen = data.get("fen")
    if not fen:
        return jsonify({"error": "fen required"}), 400

    import chess
    import chess.engine
    import os

    stockfish_path = os.getenv("STOCKFISH_PATH", "bin/stockfish")
    limit = chess.engine.Limit(time=0.1)

    try:
        board = chess.Board(fen)
        with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
            result = engine.play(board, limit)
            move = result.move
            san = board.san(move)
            board.push(move)
            return jsonify({
                "move_uci": move.uci(),
                "move_san": san,
                "fen_after": board.fen()
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()

    username = data.get("username", "").strip().lower()
    year = data.get("year")
    month = data.get("month")
    mode = data.get("mode")
    index = data.get("index")
    n = data.get("n")

    if not username or not year or not month or not mode:
        return jsonify({"error": "username, year, month, and mode are required"}), 400

    if mode not in ("single", "last_n", "all"):
        return jsonify({"error": "mode must be single, last_n, or all"}), 400

    games_key = f"games:{username}:{year}:{month}"
    summary = cache.get(games_key)

    if not summary:
        raw_games, err = fetch_games(username, year, month)
        if err:
            return jsonify({"error": err}), 404
        summary = parse_game_list(raw_games, username)
        cache.set(games_key, summary)

    selected = select_games(summary, mode, n=n, index=index)
    if not selected:
        return jsonify({"error": "No games found for the given selection"}), 404

    results = []
    for game in selected:
        game_index = game["index"]

        analysis_key = f"analysis:{username}:{year}:{month}:{game_index}"
        cached_analysis = cache.get(analysis_key)

        if cached_analysis:
            results.append({
                "game_index": game_index,
                "opponent": game["opponent"],
                "user_color": game["user_color"],
                "result": game["result"],
                "time_class": game["time_class"],
                "end_time": game["end_time"],
                "moves": cached_analysis,
                "cached": True
            })
            continue

        moves, err = analyze_game(game["pgn"], game["user_color"])
        if err:
            results.append({
                "game_index": game_index,
                "error": err
            })
            continue

        cache.set(analysis_key, moves)

        results.append({
            "game_index": game_index,
            "opponent": game["opponent"],
            "user_color": game["user_color"],
            "result": game["result"],
            "time_class": game["time_class"],
            "end_time": game["end_time"],
            "moves": moves,
            "cached": False
        })

    return jsonify({"results": results})


if __name__ == "__main__":
    app.run(debug=True)