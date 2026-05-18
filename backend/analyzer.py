
import chess
import chess.engine
import chess.pgn
import math
import io
import os
from dotenv import load_dotenv

load_dotenv()
STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", "bin/stockfish")

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

def cp_to_winpct(cp):
    cp = max(min(cp, 10000), -10000)
    return 50 + 50 * (2 / (1 + math.exp(-0.00368208 * cp)) - 1)


def classify_move(wp_loss,move_played, best_move_obj):
    if move_played == best_move_obj:
        return "best"
    elif wp_loss < 2:
        return "excellent"
    elif wp_loss < 5:
        return "great"
    elif wp_loss < 10:
        return "inaccuracy"
    elif wp_loss < 20:
        return "mistake"
    else:
        return "blunder"

def get_piece_value(board, square):
    piece = board.piece_at(square)
    if piece is None:
        return 0
    return PIECE_VALUES.get(piece.piece_type, 0)


def simple_see(board, square, attacker_color):
    target_value = get_piece_value(board, square)
    if target_value == 0:
        return 0

    attackers = board.attackers(attacker_color, square)
    if not attackers:
        return 0

    min_attacker_sq = min(attackers, key=lambda sq: get_piece_value(board, sq))
    capture_move = chess.Move(min_attacker_sq, square)
    if capture_move not in board.legal_moves:
        return 0

    board_copy = board.copy()
    board_copy.push(capture_move)
    recapture_gain = simple_see(board_copy, square, not attacker_color)

    return target_value - max(0, recapture_gain)


def detect_patterns(board_before, move, board_after):
    
    patterns = []
    opponent_color = board_after.turn  

    # 1. Check every opponent capture for material gain
    seen_squares = set()  
    for opp_move in board_after.legal_moves:
        if not board_after.is_capture(opp_move):
            continue

        target_square = opp_move.to_square
        if target_square in seen_squares:
            continue

        gain = simple_see(board_after, target_square, opponent_color)

        if gain > 0:
            seen_squares.add(target_square)
            captured_piece = board_after.piece_at(target_square)
            capturing_piece = board_after.piece_at(opp_move.from_square)
            if captured_piece and capturing_piece:
                captured_name = chess.piece_name(captured_piece.piece_type).capitalize()
                capturing_name = chess.piece_name(capturing_piece.piece_type).capitalize()
                square_name = chess.square_name(target_square)
                patterns.append(
                    f"Opponent can win your {captured_name} on {square_name} "
                    f"with {capturing_name} (net +{gain} material)"
                )

    # 2. Back rank threat
    our_color = board_before.turn
    back_rank = 0 if our_color == chess.WHITE else 7
    king_sq = board_after.king(our_color)
    if king_sq and chess.square_rank(king_sq) == back_rank:
        back_rank_squares = [chess.square(f, back_rank) for f in range(8)]
        threats = [
            sq for sq in back_rank_squares
            if board_after.piece_at(sq)
            and board_after.piece_at(sq).color != our_color
            and board_after.piece_at(sq).piece_type in [chess.ROOK, chess.QUEEN]
        ]
        if threats:
            patterns.append("Allowed back rank threat")

    return patterns

def analyze_game(pgn_string, user_color, time_per_move=0.1):
    
    game = chess.pgn.read_game(io.StringIO(pgn_string))
    if not game:
        return None, "Failed to parse PGN"

    board = game.board()
    moves_data = []
    user_color_bool = chess.WHITE if user_color == "white" else chess.BLACK
    limit = chess.engine.Limit(time=time_per_move)

    try:
        with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:

            
            info = engine.analyse(board, limit, multipv=1)
            prev_score_raw = info[0]["score"].white().score(mate_score=10000)

            for move in game.mainline_moves():
                is_user_move = (board.turn == user_color_bool)

                
                pv = info[0].get("pv", [])
                best_move_obj = pv[0] if pv else None
                best_move_san = board.san(best_move_obj) if best_move_obj else None

                board_copy = board.copy()
                pre_move_line = []
                for m in pv[:5]:
                    pre_move_line.append(board_copy.san(m))
                    board_copy.push(m)

                board_before = board.copy()
                board.push(move)

                
                info = engine.analyse(board, limit, multipv=1)
                score_after_raw = info[0]["score"].white().score(mate_score=10000)

                if user_color == "white":
                    score_before = prev_score_raw
                    score_after = score_after_raw
                else:
                    score_before = -prev_score_raw
                    score_after = -score_after_raw

                prev_score_raw = score_after_raw  

                cp_loss = score_before - score_after
                wp_before = cp_to_winpct(score_before)
                wp_after = cp_to_winpct(score_after)
                wp_loss = wp_before - wp_after

                classification = classify_move(wp_loss, move, best_move_obj) if is_user_move else None

                patterns = []
                engine_line = None

                engine_line = pre_move_line if is_user_move else None  

                if is_user_move and classification in ("inaccuracy", "mistake", "blunder"):
                    patterns = detect_patterns(board_before, move, board)

                moves_data.append({
                    "move_number": board.fullmove_number,
                    "move_san": board_before.san(move),
                    "is_user_move": is_user_move,
                    "classification": classification,       
                    "cp_loss": round(cp_loss, 1) if is_user_move else None,
                    "wp_loss": round(wp_loss, 1) if is_user_move else None,
                    "score_before": round(score_before, 1),
                    "score_after": round(score_after, 1),
                    "best_move": best_move_san if is_user_move else None,
                    "patterns": patterns,                   
                    "engine_line": engine_line,             
                })

    except Exception as e:
        return None, str(e)

    return moves_data, None