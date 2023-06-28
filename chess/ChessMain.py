import pygame as p
import ChessEngine ,ChessAI
from multiprocessing import Process, Queue

WIDTH = HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = HEIGHT
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15

Images={}
def loadImages():
    pieces = [ "wR","wN","wB","wQ","wK","bQ","bK","bB","bN","bR","bp","wp"]
    for piece in pieces:
        Images[piece] = p.transform.scale(p.image.load("images/"+piece+".png"),(SQ_SIZE,SQ_SIZE))


def main():
    p.init()
    screen = p.display.set_mode((WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    gameOver = False

    aiThinking = False
    moveUndone = False
    moveFinderProcess = None
    moveLogFont = p.font.SysFont("Arial", 14, False, False)
    p1 = False  # if a human is playing white, then this will be True, else False
    p2 = False  # if a human is playing white, then this will be True, else False


    while running :
        human_turn = (gs.whiteToMove and p1) or (not gs.whiteToMove and p2)
        if gs.whiteToMove:
            p.display.set_caption("White's Turn")
        else:
            p.display.set_caption("Black's Turn")

        
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                continue
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected ==(row,col) or col >= 8:
                        sqSelected=()
                        playerClicks=[]
                    else:
                        sqSelected=(row,col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks)==2 and human_turn:
                        move = ChessEngine.Move(playerClicks[0],playerClicks[1],gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected=()
                                playerClicks=[]
                        if not moveMade:
                            playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    if aiThinking:
                        moveFinderProcess.terminate()
                        aiThinking = False
                    moveUndone = True

                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if aiThinking:
                        moveFinderProcess.terminate()
                        aiThinking = False
                    moveUndone = True

        # AI move finder
        if not gameOver and not human_turn and not moveUndone:
            if not aiThinking:
                aiThinking = True
                return_queue = Queue()  # used to pass data between threads
                moveFinderProcess = Process(target=ChessAI.findBestMove, args=(gs, validMoves, return_queue))
                moveFinderProcess.start()

            if not moveFinderProcess.is_alive():
                ai_move = return_queue.get()
                if ai_move is None:
                    ai_move = ChessAI.findRandomMove(validMoves)
                gs.makeMove(ai_move)
                moveMade = True
                animate = True
                aiThinking = False

        
        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False
    
        drawGameState(screen,gs,validMoves,sqSelected)

        if not gameOver:
            drawMoveLog(screen, gs, moveLogFont)

        
        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                drawEndGameText(screen, "Black wins by checkmate")
            else:
                drawEndGameText(screen, "White wins by checkmate")

        elif gs.stalemate:
            gameOver = True
            drawEndGameText(screen, "Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()

def drawGameState(screen,gs,validMoves,sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen,gs.board)


def drawBoard(screen):
    global colors
    colors = [p.Color("white"),p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen,color,p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def highlightSquares(screen, gs, validMoves, sqSelected):
    """
    Highlight square selected and moves for piece selected.
    """
    if (len(gs.moveLog)) > 0:
        lastMove = gs.moveLog[-1]
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('green'))
        screen.blit(s, (lastMove.endCol * SQ_SIZE, lastMove.endRow * SQ_SIZE))
    if sqSelected != ():
        row, col = sqSelected
        if gs.board[row][col][0] == ('w' if gs.whiteToMove else 'b'):  # sqSelected is a piece that can be moved
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # transparency value 0 -> transparent, 255 -> opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))
            # highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def drawPieces(screen,board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece!= "--":
                screen.blit(Images[piece],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
    
def drawMoveLog(screen, gs, font):
    """
    Draws the move log.

    """
    movelogRect = p.Rect(WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color('black'), movelogRect)
    move_log = gs.moveLog
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + '. ' + str(move_log[i]) + " "
        if i + 1 < len(move_log):
            move_string += str(move_log[i + 1]) + "  "
        move_texts.append(move_string)

    moves_per_row = 3
    padding = 5
    line_spacing = 2
    text_y = padding
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]

        text_object = font.render(text, True, p.Color('white'))
        text_location = movelogRect.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing


def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, False, p.Color("gray"))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - text_object.get_width() / 2, HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, False, p.Color('black'))
    screen.blit(text_object, text_location.move(2, 2))

def animateMove(move, screen, board, clock):
    """
    Animating a move
    """
    global colors
    d_row = move.endRow - move.startRow
    d_col = move.endCol - move.startCol
    frames_per_square = 10  # frames to move one square
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square
    for frame in range(frame_count + 1):
        row, col = (move.startRow + d_row * frame / frame_count, move.startCol + d_col * frame / frame_count)
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        end_square = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        # draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            if move.is_enpassant_move:
                enpassant_row = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                end_square = p.Rect(move.endCol * SQ_SIZE, enpassant_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(Images[move.pieceCaptured], end_square)
        # draw moving piece
        screen.blit(Images[move.pieceMoved], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

if __name__ =="__main__": 
    main()