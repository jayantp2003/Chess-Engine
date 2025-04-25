"""
Handling the AI moves.
"""
import random
import multiprocessing
from multiprocessing import Pool, cpu_count, Queue
import copy
import time
import logging
import os

# Set up logging
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(log_dir, "chess_ai.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w"
)
logger = logging.getLogger("ChessAI")

# Global variables for UI display
currentDepth = 0
nodesEvaluated = 0
alphaCount = 0
pruningPercent = 0
lastMoveScore = 0
bestMoveSoFar = None

# Statistics tracking
ai_stats = {
    "positions_evaluated": 0,
    "max_depth_reached": 0,
    "alpha_beta_cutoffs": 0,
    "time_spent": 0,
    "moves_considered": 0,
    "avg_branching_factor": 0,
    "best_move_scores": {},
    "parallel_efficiency": 0,
    "nodes_for_current_move": 0,  # Nodes evaluated for the current move
    "nodes_pruned_for_current_move": 0  # Nodes pruned for the current move
}

# Reset stats for new move calculation
def reset_stats():
    global ai_stats
    ai_stats = {
        "positions_evaluated": 0,
        "max_depth_reached": 0,
        "alpha_beta_cutoffs": 0,
        "time_spent": 0,
        "moves_considered": 0,
        "avg_branching_factor": 0,
        "best_move_scores": {},
        "parallel_efficiency": 0,
        "nodes_for_current_move": 0,
        "nodes_pruned_for_current_move": 0
    }

# Enhanced piece values - more nuanced than before
pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3.25, "N": 3.25, "p": 1}

knightScore = [[0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
                 [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
                 [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
                 [0.2, 0.55, 0.65, 0.7, 0.7, 0.65, 0.55, 0.2],
                 [0.2, 0.5, 0.65, 0.7, 0.7, 0.65, 0.5, 0.2],
                 [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
                 [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
                 [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]]

bishopScore = [[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
                 [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                 [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
                 [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
                 [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                 [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
                 [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
                 [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]]

rookScore = [[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
               [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]]

queenScore = [[0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
                [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]]

pawnScore = [[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
               [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
               [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
               [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
               [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
               [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
               [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
               [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]]

piecePositionScore = {"wN": knightScore,
                         "bN": knightScore[::-1],
                         "wB": bishopScore,
                         "bB": bishopScore[::-1],
                         "wQ": queenScore,
                         "bQ": queenScore[::-1],
                         "wR": rookScore,
                         "bR": rookScore[::-1],
                         "wp": pawnScore,
                         "bp": pawnScore[::-1]}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 5
# Number of worker processes to use (adjust based on CPU cores)
NUM_WORKERS = max(1, cpu_count() - 1)


def findBestMove(gs, validMoves, return_queue):
    """
    Use multiprocessing to find the best move using parallel alpha-beta search
    """
    global ai_stats
    start_time = time.time()
    reset_stats()
    
    logger.info(f"Starting AI move computation with {NUM_WORKERS} workers")
    logger.info(f"Initial position evaluation: {scoreBoard(gs)}")
    logger.info(f"Valid moves count: {len(validMoves)}")
    
    if not validMoves:
        logger.warning("No valid moves available")
        return_queue.put((None, ai_stats))
        return
    
    random.shuffle(validMoves)
    ai_stats["moves_considered"] = len(validMoves)
    
    # For very small number of moves, use sequential search
    if len(validMoves) <= 2:
        logger.info("Using sequential search due to small number of moves")
        best_move = findBestMoveSequential(gs, validMoves)
        end_time = time.time()
        ai_stats["time_spent"] = end_time - start_time
        log_move_stats(best_move)
        return_queue.put((best_move, ai_stats))
        return
    
    seq_start_time = time.time()
    # Estimate sequential time for comparison
    seq_positions = estimate_sequential_positions(gs, validMoves)
    seq_time_estimate = (time.time() - seq_start_time) * seq_positions / 100  # Estimate based on sample
    
    # Split moves among workers
    with Pool(processes=NUM_WORKERS) as pool:
        # Create a list of tuples with game state and moves for each worker
        move_chunks = []
        chunk_size = max(1, len(validMoves) // NUM_WORKERS)
        
        logger.info(f"Dividing {len(validMoves)} moves into {NUM_WORKERS} chunks of approximately {chunk_size} moves each")
        
        for i in range(0, len(validMoves), chunk_size):
            # Make a deep copy of the game state for each worker
            gs_copy = copy.deepcopy(gs)
            # Get a chunk of moves for this worker
            move_subset = validMoves[i:i+chunk_size]
            move_chunks.append((gs_copy, move_subset))
        
        # Map the evaluation function to each chunk of moves
        results = pool.map(evaluateMoveSet, move_chunks)
    
    # Combine statistics from workers
    positions_evaluated = 0
    cutoffs = 0
    for result in results:
        if len(result) > 2:  # Contains stats
            worker_stats = result[2]
            positions_evaluated += worker_stats.get("positions_evaluated", 0)
            cutoffs += worker_stats.get("alpha_beta_cutoffs", 0)
    
    ai_stats["positions_evaluated"] = positions_evaluated
    ai_stats["alpha_beta_cutoffs"] = cutoffs
    
    # Find the best move from all results
    best_score = -CHECKMATE
    best_move = None
    
    for result in results:
        move = result[0]
        score = result[1]
        logger.info(f"Worker evaluated move {move} with score {score}")
        
        if move and score > best_score:
            best_score = score
            best_move = move
    
    end_time = time.time()
    ai_stats["time_spent"] = end_time - start_time
    
    # Calculate parallel efficiency if we have a sequential estimate
    if seq_time_estimate > 0:
        ai_stats["parallel_efficiency"] = seq_time_estimate / ((end_time - start_time) * NUM_WORKERS)
        logger.info(f"Parallel efficiency: {ai_stats['parallel_efficiency']:.2f}x")
    
    log_move_stats(best_move)
    # Return both the best move and the stats dictionary
    return_queue.put((best_move, ai_stats))


def estimate_sequential_positions(gs, validMoves, sample_size=3):
    """Estimate the number of positions that would be evaluated sequentially"""
    sample = validMoves[:min(sample_size, len(validMoves))]
    positions = 0
    
    for move in sample:
        gs_copy = copy.deepcopy(gs)
        gs_copy.makeMove(move)
        next_moves = gs_copy.getValidMoves()
        # Just count first level branching
        positions += len(next_moves)
    
    # Extrapolate to all moves
    return positions * len(validMoves) / len(sample)


def log_move_stats(best_move):
    """Log comprehensive statistics about the AI's decision"""
    logger.info("=" * 50)
    logger.info(f"CHESS AI ANALYSIS REPORT")
    logger.info("=" * 50)
    logger.info(f"Best move selected: {best_move}")
    logger.info(f"Total positions evaluated: {ai_stats['positions_evaluated']:,}")
    logger.info(f"Alpha-beta cutoffs: {ai_stats['alpha_beta_cutoffs']:,}")
    logger.info(f"Pruning efficiency: {ai_stats['alpha_beta_cutoffs'] / max(1, ai_stats['positions_evaluated']):.2%}")
    logger.info(f"Time spent: {ai_stats['time_spent']:.4f} seconds")
    logger.info(f"Positions per second: {ai_stats['positions_evaluated'] / max(0.001, ai_stats['time_spent']):,.2f}")
    
    if ai_stats.get("parallel_efficiency"):
        logger.info(f"Parallel speedup: {ai_stats['parallel_efficiency']:.2f}x with {NUM_WORKERS} workers")
    
    logger.info("=" * 50)


def evaluateMoveSet(args):
    """
    Helper function to evaluate a set of moves in a worker process
    Returns the best move and its score from this set
    """
    gs, moves = args
    best_score = -CHECKMATE
    best_move = None
    
    # Local stats for this worker
    worker_stats = {
        "positions_evaluated": 0,
        "alpha_beta_cutoffs": 0,
        "depth_reached": []
    }
    
    for move in moves:
        # Track move evaluation
        move_str = str(move)
        
        gs.makeMove(move)
        next_moves = gs.getValidMoves()
        
        # Use negamax with the standard depth
        score, stats = findMoveNegaMaxAlphaBeta(
            gs, next_moves, DEPTH-1, -CHECKMATE, CHECKMATE, 
            -1 if gs.whiteToMove else 1, worker_stats
        )
        score = -score  # Negate score from opponent's perspective
        
        worker_stats["positions_evaluated"] += stats["positions_evaluated"]
        worker_stats["alpha_beta_cutoffs"] += stats["alpha_beta_cutoffs"]
        
        gs.undoMove()
        
        if score > best_score:
            best_score = score
            best_move = move
    
    return (best_move, best_score, worker_stats)


def findBestMoveSequential(gs, validMoves):
    """
    Original sequential implementation for small move sets or fallback
    """
    global nextMove, ai_stats
    nextMove = None
    
    logger.info("Using sequential negamax alpha-beta search")
    
    # First pass to calculate stats
    worker_stats = {
        "positions_evaluated": 0,
        "alpha_beta_cutoffs": 0,
        "depth_reached": []
    }
    
    _, stats = findMoveNegaMaxAlphaBeta(
        gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE,
        1 if gs.whiteToMove else -1, worker_stats
    )
    
    ai_stats["positions_evaluated"] = stats["positions_evaluated"]
    ai_stats["alpha_beta_cutoffs"] = stats["alpha_beta_cutoffs"]
    ai_stats["max_depth_reached"] = DEPTH
    
    return nextMove


def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier, stats=None):
    """
    NegaMax algorithm with alpha-beta pruning and enhanced statistics tracking
    """
    global nextMove
    
    # Initialize local stats if not provided
    if stats is None:
        stats = {
            "positions_evaluated": 0,
            "alpha_beta_cutoffs": 0,
            "depth_reached": []
        }
    
    # Base case - reached a leaf node
    if depth == 0:
        stats["positions_evaluated"] += 1
        stats["depth_reached"].append(DEPTH - depth)
        return turnMultiplier * scoreBoard(gs), stats
    
    maxScore = -CHECKMATE
    original_alpha = alpha
    move_count = 0
    pruned_count = 0
    
    for move in validMoves:
        move_count += 1
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        
        score, substats = findMoveNegaMaxAlphaBeta(
            gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier, stats
        )
        score = -score  # Negate score from opponent's perspective
        
        # Roll up statistics from subtree
        stats["positions_evaluated"] = substats["positions_evaluated"]
        stats["alpha_beta_cutoffs"] = substats["alpha_beta_cutoffs"]
        
        gs.undoMove()
        
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        
        # Alpha-beta pruning
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            stats["alpha_beta_cutoffs"] += (len(validMoves) - move_count)
            pruned_count += (len(validMoves) - move_count)
            break
    
    return maxScore, stats


def scoreBoard(gs):
    """
    Enhanced scoring function with more advanced evaluation factors.
    A positive score is good for white, a negative score is good for black.
    """
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE  # white wins
    elif gs.stalemate:
        return STALEMATE
    
    score = 0
    
    # 1. Material and piece position
    for row in range(len(gs.board)):
        for col in range(len(gs.board[0])):
            piece = gs.board[row][col]
            if piece != "--":
                # Basic material value and position score
                piece_position_score = 0
                if piece[1] != "K":
                    piece_position_score = piecePositionScore[piece][row][col]
                
                # Apply multiplier to position scores in endgame
                if is_endgame(gs):
                    # Emphasize piece positioning more in endgame
                    piece_position_score *= 1.5
                
                if piece[0] == "w":
                    score += pieceScore[piece[1]] + piece_position_score
                else:
                    score -= pieceScore[piece[1]] + piece_position_score
    
    # 2. Mobility - more moves is better (simplified version)
    if gs.whiteToMove:
        score += len(gs.getValidMoves()) * 0.1
    else:
        score -= len(gs.getValidMoves()) * 0.1
    
    # 3. Pawn structure - doubled/isolated pawns penalty
    # (just a simplified version for demonstration)
    score += evaluate_pawn_structure(gs)
    
    # 4. King safety - penalize exposed king
    score += evaluate_king_safety(gs)
    
    # 5. Control of center
    score += evaluate_center_control(gs)
    
    # Return score from perspective of current player
    return score

def is_endgame(gs):
    """
    Determine if the position is in an endgame stage.
    Typical endgame indicators: few pieces, no queens, etc.
    """
    white_pieces = 0
    black_pieces = 0
    white_has_queen = False
    black_has_queen = False
    
    for row in range(len(gs.board)):
        for col in range(len(gs.board[0])):
            piece = gs.board[row][col]
            if piece != "--":
                if piece[0] == "w":
                    white_pieces += 1
                    if piece[1] == "Q":
                        white_has_queen = True
                elif piece[0] == "b":
                    black_pieces += 1
                    if piece[1] == "Q":
                        black_has_queen = True
    
    # If both sides have few pieces or no queens, consider it endgame
    total_pieces = white_pieces + black_pieces
    return total_pieces <= 12 or (not white_has_queen and not black_has_queen)

def evaluate_pawn_structure(gs):
    """
    Evaluate the pawn structure - penalize doubled/isolated pawns.
    """
    score = 0
    
    # Count pawns in each column
    white_pawn_columns = [0] * 8
    black_pawn_columns = [0] * 8
    
    for row in range(8):
        for col in range(8):
            piece = gs.board[row][col]
            if piece == "wp":
                white_pawn_columns[col] += 1
            elif piece == "bp":
                black_pawn_columns[col] += 1
    
    # Penalize doubled pawns
    for col in range(8):
        if white_pawn_columns[col] > 1:
            score -= 0.5 * (white_pawn_columns[col] - 1)
        if black_pawn_columns[col] > 1:
            score += 0.5 * (black_pawn_columns[col] - 1)
    
    # Penalize isolated pawns (pawns with no friendly pawns in adjacent columns)
    for col in range(8):
        if white_pawn_columns[col] > 0:
            isolated = True
            if col > 0 and white_pawn_columns[col-1] > 0:
                isolated = False
            if col < 7 and white_pawn_columns[col+1] > 0:
                isolated = False
            if isolated:
                score -= 0.3
        
        if black_pawn_columns[col] > 0:
            isolated = True
            if col > 0 and black_pawn_columns[col-1] > 0:
                isolated = False
            if col < 7 and black_pawn_columns[col+1] > 0:
                isolated = False
            if isolated:
                score += 0.3
    
    return score

def evaluate_king_safety(gs):
    """
    Evaluate king safety - penalize exposed kings.
    """
    score = 0
    
    # Get king positions
    white_king_row, white_king_col = gs.whiteKingLocation
    black_king_row, black_king_col = gs.blackKingLocation
    
    # Count pieces around kings (simplified king safety)
    white_king_defenders = count_pieces_around(gs, white_king_row, white_king_col, "w")
    black_king_defenders = count_pieces_around(gs, black_king_row, black_king_col, "b")
    
    # In the opening/middlegame, reward having pieces around your king
    if not is_endgame(gs):
        score += 0.2 * white_king_defenders
        score -= 0.2 * black_king_defenders
    else:
        # In endgame, king should be active
        # Reward centralized king in endgame
        white_king_center_distance = distance_to_center(white_king_row, white_king_col)
        black_king_center_distance = distance_to_center(black_king_row, black_king_col)
        
        score -= 0.05 * white_king_center_distance
        score += 0.05 * black_king_center_distance
    
    return score

def count_pieces_around(gs, row, col, color):
    """
    Count friendly pieces in the 3x3 square around a given position.
    """
    count = 0
    for r in range(max(0, row-1), min(8, row+2)):
        for c in range(max(0, col-1), min(8, col+2)):
            if gs.board[r][c] != "--" and gs.board[r][c][0] == color:
                count += 1
    
    # Don't count the king itself
    return count - 1  # -1 to exclude the king itself

def distance_to_center(row, col):
    """
    Calculate the distance from a square to the center of the board.
    """
    center_row, center_col = 3.5, 3.5  # Center between squares
    return abs(row - center_row) + abs(col - center_col)

def evaluate_center_control(gs):
    """
    Evaluate control of the center of the board.
    """
    score = 0
    
    # Define center squares
    center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
    
    # Count pieces in the center
    for row, col in center_squares:
        piece = gs.board[row][col]
        if piece != "--":
            # Reward for controlling center with pieces
            if piece[0] == "w":
                score += 0.2
            else:
                score -= 0.2
    
    return score


def findRandomMove(validMoves):
    return random.choice(validMoves)
