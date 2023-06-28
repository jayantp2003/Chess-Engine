class GameState:
    def __init__(self):
        """
        This is the initialization method for a chess board. It sets up the initial state of the board with the pieces in their starting positions.
        """
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.moveFunctions = {
            "p": self.getPawnMoves,
            "R": self.getRookMoves,
            "N": self.getKnightMoves,
            "B": self.getBishopMoves,
            "Q": self.getQueenMoves,
            "K": self.getKingMoves,
        }
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.in_check = False
        self.pins = []
        self.checks = []
        self.enpassant_possible = ()
        self.enpassant_possible_log = [self.enpassant_possible]
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [
            CastleRights(
                self.current_castling_rights.wks,
                self.current_castling_rights.bks,
                self.current_castling_rights.wqs,
                self.current_castling_rights.bqs,
            )
        ]

    def makeMove(self, move):
        """
        Update the chess board after a move is made.
        """

        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        if move.is_pawn_promotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        if move.is_enpassant_move:
            self.board[move.startRow][move.endCol] = "--"

        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
            self.enpassant_possible = (
                (move.startRow + move.endRow) // 2,
                move.startCol,
            )
        else:
            self.enpassant_possible = ()

        if move.is_castle_move:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][
                    move.endCol + 1
                ]
                self.board[move.endRow][move.endCol + 1] = "--"
            else:
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][
                    move.endCol - 2
                ]
                self.board[move.endRow][move.endCol - 2] = "--"  

        self.enpassant_possible_log.append(self.enpassant_possible)

        self.updateCastleRights(move)
        self.castle_rights_log.append(
            CastleRights(
                self.current_castling_rights.wks,
                self.current_castling_rights.bks,
                self.current_castling_rights.wqs,
                self.current_castling_rights.bqs,
            )
        )

    def undoMove(self):
        """
        Undo the last move made in the chess game.
        """

        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove 
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            if move.is_enpassant_move:
                self.board[move.endRow][move.endCol] = "--" 
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enpassant_possible_log.pop()
            self.enpassant_possible = self.enpassant_possible_log[-1]

            self.castle_rights_log.pop()
            self.current_castling_rights = self.castle_rights_log[-1]  
            if move.is_castle_move:
                if move.endCol - move.startCol == 2: 
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][
                        move.endCol - 1
                    ]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else: 
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][
                        move.endCol + 1
                    ]
                    self.board[move.endRow][move.endCol + 1] = "--"
            self.checkmate = False
            self.stalemate = False

    def updateCastleRights(self, move):
        """
        Update the castle rights based on the given move.
        """

        if move.pieceCaptured == "wR":
            if move.endCol == 0:  
                self.current_castling_rights.wqs = False
            elif move.endCol == 7:  
                self.current_castling_rights.wks = False
        elif move.pieceCaptured == "bR":
            if move.endCol == 0: 
                self.current_castling_rights.bqs = False
            elif move.endCol == 7:
                self.current_castling_rights.bks = False

        if move.pieceMoved == "wK":
            self.current_castling_rights.wqs = False
            self.current_castling_rights.wks = False
        elif move.pieceMoved == "bK":
            self.current_castling_rights.bqs = False
            self.current_castling_rights.bks = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0: 
                    self.current_castling_rights.wqs = False
                elif move.startCol == 7: 
                    self.current_castling_rights.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0: 
                    self.current_castling_rights.bqs = False
                elif move.startCol == 7:  
                    self.current_castling_rights.bks = False

    def getValidMoves(self):
        """
        Get all the valid moves for the current player in the chess game.
        return A list of valid moves
        """

        temp_castle_rights = CastleRights(
            self.current_castling_rights.wks,
            self.current_castling_rights.bks,
            self.current_castling_rights.wqs,
            self.current_castling_rights.bqs,
        )
        moves = []
        self.in_check, self.pins, self.checks = self.checkForPinsAndChecks()

        if self.whiteToMove:
            king_row = self.whiteKingLocation[0]
            king_col = self.whiteKingLocation[1]
        else:
            king_row = self.blackKingLocation[0]
            king_col = self.blackKingLocation[1]
        if self.in_check:
            if len(self.checks) == 1:  
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []
                if piece_checking[1] == "N":
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (
                            king_row + check[2] * i,
                            king_col + check[3] * i,
                        )
                        valid_squares.append(valid_square)
                        if (valid_square[0] == check_row and valid_square[1] == check_col):  
                            break
                for i in range(len(moves) - 1, -1, -1):
                    if (moves[i].pieceMoved[1] != "K"): 
                        if (not (moves[i].endRow, moves[i].endCol) in valid_squares):
                            moves.remove(moves[i])
            else:  
                self.getKingMoves(king_row, king_col, moves)
        else:  
            moves = self.getAllPossibleMoves()
            if self.whiteToMove:
                self.getCastleMoves(
                    self.whiteKingLocation[0], self.whiteKingLocation[1], moves
                )
            else:
                self.getCastleMoves(
                    self.blackKingLocation[0], self.blackKingLocation[1], moves
                )

        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.current_castling_rights = temp_castle_rights
        return moves

    def inCheck(self):
        """
        Check if the current player is in check.
        return True if the current player is in check, False otherwise.
        """

        if self.whiteToMove:
            return self.squareUnderAttack(
                self.whiteKingLocation[0], self.whiteKingLocation[1]
            )
        else:
            return self.squareUnderAttack(
                self.blackKingLocation[0], self.blackKingLocation[1]
            )

    def squareUnderAttack(self, row, col):
        """
        Check if a square on the chessboard is under attack by the opponent.
        return True if the square is under attack, False otherwise
        """

        self.whiteToMove = not self.whiteToMove 
        opponents_moves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in opponents_moves:
            if move.endRow == row and move.endCol == col:  
                return True
        return False

    def getAllPossibleMoves(self):
        """
        Get all possible moves for the current player in the chess game.
        return A list of all possible moves
        """
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == "w" and self.whiteToMove) or (
                    turn == "b" and not self.whiteToMove
                ):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](
                        row, col, moves
                    )  
        return moves

    def checkForPinsAndChecks(self):
        """
        Check if there are any pins or checks on the current chessboard state.
        return pins - a list of pinned pieces
        return checks - a list of pieces that are checking the king
        return in_check - a boolean indicating if the king is in check
        """

        pins = []  
        checks = []  
        in_check = False
        if self.whiteToMove:
            enemy_color = "b"
            ally_color = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        
        directions = (
            (-1, 0),
            (0, -1),
            (1, 0),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        )
        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()  # reset possible pins
            for i in range(1, 8):
                endRow = startRow + direction[0] * i
                endCol = startCol + direction[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    end_piece = self.board[endRow][endCol]
                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        if possible_pin == ():  # first allied piece could be pinned
                            possible_pin = (endRow, endCol, direction[0], direction[1])
                        else:  # 2nd allied piece - no check or pin from this direction
                            break
                    elif end_piece[0] == enemy_color:
                        enemy_type = end_piece[1]
                        
                        # 5 possibilities in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king
                        if (
                            (0 <= j <= 3 and enemy_type == "R")
                            or (4 <= j <= 7 and enemy_type == "B")
                            or (
                                i == 1
                                and enemy_type == "p"
                                and (
                                    (enemy_color == "w" and 6 <= j <= 7)
                                    or (enemy_color == "b" and 4 <= j <= 5)
                                )
                            )
                            or (enemy_type == "Q")
                            or (i == 1 and enemy_type == "K")
                        ):
                            if possible_pin == ():  # no piece blocking, so check
                                in_check = True
                                checks.append(
                                    (endRow, endCol, direction[0], direction[1])
                                )
                                break
                            else:  # piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece not applying checks
                            break
                else:
                    break  # off board
        # check for knight checks
        knight_moves = (
            (-2, -1),
            (-2, 1),
            (-1, 2),
            (1, 2),
            (2, -1),
            (2, 1),
            (-1, -2),
            (1, -2),
        )
        for move in knight_moves:
            endRow = startRow + move[0]
            endCol = startCol + move[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                end_piece = self.board[endRow][endCol]
                if (
                    end_piece[0] == enemy_color and end_piece[1] == "N"
                ):  # enemy knight attacking a king
                    in_check = True
                    checks.append((endRow, endCol, move[0], move[1]))
        return in_check, pins, checks

    def getPawnMoves(self, row, col, moves):
        """
        Get all the pawn moves for the pawn located at row, col and add the moves to the list.
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            move_amount = -1
            startRow = 6
            enemy_color = "b"
            king_row, king_col = self.whiteKingLocation
        else:
            move_amount = 1
            startRow = 1
            enemy_color = "w"
            king_row, king_col = self.blackKingLocation

        if self.board[row + move_amount][col] == "--":  # 1 square pawn advance
            if not piece_pinned or pin_direction == (move_amount, 0):
                moves.append(Move((row, col), (row + move_amount, col), self.board))
                if (
                    row == startRow and self.board[row + 2 * move_amount][col] == "--"
                ):  # 2 square pawn advance
                    moves.append(
                        Move((row, col), (row + 2 * move_amount, col), self.board)
                    )
        if col - 1 >= 0:  # capture to the left
            if not piece_pinned or pin_direction == (move_amount, -1):
                if self.board[row + move_amount][col - 1][0] == enemy_color:
                    moves.append(
                        Move((row, col), (row + move_amount, col - 1), self.board)
                    )
                if (row + move_amount, col - 1) == self.enpassant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            inside_range = range(king_col + 1, col - 1)
                            outside_range = range(col + 1, 8)
                        else:  # king right of the pawn
                            inside_range = range(king_col - 1, col, -1)
                            outside_range = range(col - 2, -1, -1)
                        for i in inside_range:
                            if (
                                self.board[row][i] != "--"
                            ):  # some piece beside en-passant pawn blocks
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == enemy_color and (
                                square[1] == "R" or square[1] == "Q"
                            ):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(
                            Move(
                                (row, col),
                                (row + move_amount, col - 1),
                                self.board,
                                is_enpassant_move=True,
                            )
                        )
        if col + 1 <= 7:  # capture to the right
            if not piece_pinned or pin_direction == (move_amount, +1):
                if self.board[row + move_amount][col + 1][0] == enemy_color:
                    moves.append(
                        Move((row, col), (row + move_amount, col + 1), self.board)
                    )
                if (row + move_amount, col + 1) == self.enpassant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            inside_range = range(king_col + 1, col)
                            outside_range = range(col + 2, 8)
                        else:  # king right of the pawn
                            inside_range = range(king_col - 1, col + 1, -1)
                            outside_range = range(col - 1, -1, -1)
                        for i in inside_range:
                            if (
                                self.board[row][i] != "--"
                            ):  # some piece beside en-passant pawn blocks
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == enemy_color and (
                                square[1] == "R" or square[1] == "Q"
                            ):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(
                            Move(
                                (row, col),
                                (row + move_amount, col + 1),
                                self.board,
                                is_enpassant_move=True,
                            )
                        )

    def getRookMoves(self, row, col, moves):
        """
        Get all the rook moves for the rook located at row, col and add the moves to the list.
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if (
                    self.board[row][col][1] != "Q"
                ):  # can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        enemy_color = "b" if self.whiteToMove else "w"
        for direction in directions:
            for i in range(1, 8):
                endRow = row + direction[0] * i
                endCol = col + direction[1] * i
                if (
                    0 <= endRow <= 7 and 0 <= endCol <= 7
                ):  # check for possible moves only in boundaries of the board
                    if (
                        not piece_pinned
                        or pin_direction == direction
                        or pin_direction == (-direction[0], -direction[1])
                    ):
                        end_piece = self.board[endRow][endCol]
                        if end_piece == "--":  # empty space is valid
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        elif end_piece[0] == enemy_color:  # capture enemy piece
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break
                        else:  # friendly piece
                            break
                else:  # off board
                    break

    def getKnightMoves(self, row, col, moves):
        """
        Get all the knight moves for the knight located at row col and add the moves to the list.
        """
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        knight_moves = (
            (-2, -1),
            (-2, 1),
            (-1, 2),
            (1, 2),
            (2, -1),
            (2, 1),
            (-1, -2),
            (1, -2),
        )  # up/left up/right right/up right/down down/left down/right left/up left/down
        ally_color = "w" if self.whiteToMove else "b"
        for move in knight_moves:
            endRow = row + move[0]
            endCol = col + move[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                if not piece_pinned:
                    end_piece = self.board[endRow][endCol]
                    if (
                        end_piece[0] != ally_color
                    ):  # so its either enemy piece or empty square
                        moves.append(Move((row, col), (endRow, endCol), self.board))

    def getBishopMoves(self, row, col, moves):
        """
        Get all the bishop moves for the bishop located at row col and add the moves to the list.
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = (
            (-1, -1),
            (-1, 1),
            (1, 1),
            (1, -1),
        )  # diagonals: up/left up/right down/right down/left
        enemy_color = "b" if self.whiteToMove else "w"
        for direction in directions:
            for i in range(1, 8):
                endRow = row + direction[0] * i
                endCol = col + direction[1] * i
                if (
                    0 <= endRow <= 7 and 0 <= endCol <= 7
                ):  # check if the move is on board
                    if (
                        not piece_pinned
                        or pin_direction == direction
                        or pin_direction == (-direction[0], -direction[1])
                    ):
                        end_piece = self.board[endRow][endCol]
                        if end_piece == "--":  # empty space is valid
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        elif end_piece[0] == enemy_color:  # capture enemy piece
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break
                        else:  # friendly piece
                            break
                else:  # off board
                    break

    def getQueenMoves(self, row, col, moves):
        """
        Get all the queen moves for the queen located at row col and add the moves to the list.
        """
        self.getBishopMoves(row, col, moves)
        self.getRookMoves(row, col, moves)

    def getKingMoves(self, row, col, moves):
        """
        Get all the king moves for the king located at row col and add the moves to the list.
        """
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = row + row_moves[i]
            endCol = col + col_moves[i]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                end_piece = self.board[endRow][endCol]
                if end_piece[0] != ally_color:  # not an ally piece - empty or enemy
                    # place king on end square and check for checks
                    if ally_color == "w":
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    in_check, pins, checks = self.checkForPinsAndChecks()
                    if not in_check:
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    # place king back on original location
                    if ally_color == "w":
                        self.whiteKingLocation = (row, col)
                    else:
                        self.blackKingLocation = (row, col)

    def getCastleMoves(self, row, col, moves):
        """
        Generate all valid castle moves for the king at (row, col) and add them to the list of moves.
        """
        if self.squareUnderAttack(row, col):
            return  # can't castle while in check
        if (self.whiteToMove and self.current_castling_rights.wks) or (
            not self.whiteToMove and self.current_castling_rights.bks
        ):
            self.getKingsideCastleMoves(row, col, moves)
        if (self.whiteToMove and self.current_castling_rights.wqs) or (
            not self.whiteToMove and self.current_castling_rights.bqs
        ):
            self.getQueensideCastleMoves(row, col, moves)

    def getKingsideCastleMoves(self, row, col, moves):
        """
        Given the current state of the chess board, the row and column of a piece, and a list of possible moves, check if a kingside castle move is possible. If it is, add the move to the list of moves.
        """
        if self.board[row][col + 1] == "--" and self.board[row][col + 2] == "--":
            if not self.squareUnderAttack(row, col + 1) and not self.squareUnderAttack(
                row, col + 2
            ):
                moves.append(
                    Move((row, col), (row, col + 2), self.board, is_castle_move=True)
                )

    def getQueensideCastleMoves(self, row, col, moves):
        """
        Given the current position of a piece on the chessboard, check if queenside castle move is possible. If the squares to the left of the piece are empty and not under attack, add the move to the list of possible moves.
        """

        if (
            self.board[row][col - 1] == "--"
            and self.board[row][col - 2] == "--"
            and self.board[row][col - 3] == "--"
        ):
            if not self.squareUnderAttack(row, col - 1) and not self.squareUnderAttack(
                row, col - 2
            ):
                moves.append(
                    Move((row, col), (row, col - 2), self.board, is_castle_move=True)
                )


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(
        self,
        start_square,
        end_square,
        board,
        is_enpassant_move=False,
        is_castle_move=False,
    ):
        self.startRow = start_square[0]
        self.startCol = start_square[1]
        self.endRow = end_square[0]
        self.endCol = end_square[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.is_pawn_promotion = (self.pieceMoved == "wp" and self.endRow == 0) or (
            self.pieceMoved == "bp" and self.endRow == 7
        )
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"
        self.is_castle_move = is_castle_move

        self.is_capture = self.pieceCaptured != "--"
        self.moveID = (
            self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        )

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotations(self):
        if self.is_pawn_promotion:
            return self.getRankFile(self.endRow, self.endCol) + "Q"
        if self.is_castle_move:
            if self.endCol == 1:
                return "0-0-0"
            else:
                return "0-0"
        if self.is_enpassant_move:
            return (
                self.getRankFile(self.startRow, self.startCol)[0]
                + "x"
                + self.getRankFile(self.endRow, self.endCol)
                + " e.p."
            )
        if self.pieceCaptured != "--":
            if self.pieceMoved[1] == "p":
                return (
                    self.getRankFile(self.startRow, self.startCol)[0]
                    + "x"
                    + self.getRankFile(self.endRow, self.endCol)
                )
            else:
                return (
                    self.pieceMoved[1]
                    + "x"
                    + self.getRankFile(self.endRow, self.endCol)
                )
        else:
            if self.pieceMoved[1] == "p":
                return self.getRankFile(self.endRow, self.endCol)
            else:
                return self.pieceMoved[1] + self.getRankFile(self.endRow, self.endCol)
            
    def getRankFile(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]

    def __str__(self):
        if self.is_castle_move:
            return "0-0" if self.endCol == 6 else "0-0-0"

        end_square = self.getRankFile(self.endRow, self.endCol)

        if self.pieceMoved[1] == "p":
            if self.is_capture:
                return self.cols_to_files[self.startCol] + "x" + end_square
            else:
                return end_square + "Q" if self.is_pawn_promotion else end_square

        move_string = self.pieceMoved[1]
        if self.is_capture:
            move_string += "x"
        return move_string + end_square
