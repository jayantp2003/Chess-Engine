# to store information about the chess game
# Determining the valid moves at the current state

class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.moveFunctions = {'p':self.getPawnMoves,'R':self.getRockMoves,'N':self.getKnightMoves
                              ,'B':self.getBishopMoves,'Q':self.getQueenMoves,'K':self.getKingMoves}

        self.whiteToMove = True
        self.moveLog = []

    def makeMove(self,move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
    
    def undoMove(self):
        if len(self.moveLog) !=0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured


    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[0])):
                turn  = self.board[r][c][0]
                if(turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves)
        return moves

    def getValidMoves(self):
        return self.getAllPossibleMoves()


    def getPawnMoves(self,r,c,moves):
        if self.whiteToMove:
            if(r>=1 and self.board[r-1][c]=="--"):
                moves.append(Move((r,c),(r-1,c),self.board))
                if r==6 and self.board[r-2][c] == '--':
                    moves.append(Move((r,c),(r-2,c),self.board))
            
            if(r>0 and c>0 and self.board[r-1][c-1]!="--"):
                moves.append(Move((r,c),(r-1,c-1),self.board))
            if(r>0 and c<7 and self.board[r-1][c+1]!="--"):
                moves.append(Move((r,c),(r-1,c+1),self.board))
        
        else:
            if(r<7 and self.board[r+1][c]=="--"):
                moves.append(Move((r,c),(r+1,c),self.board))
                if r==1 and self.board[r+2][c] == '--':
                    moves.append(Move((r,c),(r+2,c),self.board))
            
            if(r<7 and c>0 and self.board[r+1][c-1]!="--"):
                moves.append(Move((r,c),(r+1,c-1),self.board))
            if(r<7 and c<7 and self.board[r+1][c+1]!="--"):
                moves.append(Move((r,c),(r+1,c+1),self.board))

    def getRockMoves(self,r,c,moves):
        dir = {(0,1),(1,0),(0,-1),(-1,0)}

        for (x,y) in dir:
            r1 = r
            c1 = c
            while(r1+x<=7 and c1+y <=7 and r1+x>=0 and c1+y>=0):
                if(self.board[r1+x][c1+y]=='--'):
                    moves.append(Move((r,c),(r1+x,c1+y),self.board))
                else:
                    if(self.board[r1+x][c1+y][0]=='b' and self.whiteToMove) or (self.board[r1+x][c1+y][0]=='w' and not self.whiteToMove):
                        moves.append(Move((r,c),(r1+x,c1+y),self.board))
                    break
                r1 = r1+x
                c1 = c1+y  

    def getBishopMoves(self,r,c,moves):
        dir = {(1,1),(1,-1),(-1,1),(-1,-1)}

        for (x,y) in dir:
            r1 = r
            c1 = c
            while(r1+x<=7 and c1+y <=7 and r1+x>=0 and c1+y>=0):
                if(self.board[r1+x][c1+y]=='--'):
                    moves.append(Move((r,c),(r1+x,c1+y),self.board))
                else:
                    if(self.board[r1+x][c1+y][0]=='b' and self.whiteToMove) or (self.board[r1+x][c1+y][0]=='w' and not self.whiteToMove):
                        moves.append(Move((r,c),(r1+x,c1+y),self.board))
                    break
                r1 = r1+x
                c1 = c1+y  

    def getQueenMoves(self,r,c,moves):
        dir = {(0,1),(1,0),(0,-1),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)}

        for (x,y) in dir:
            r1 = r
            c1 = c
            while(r1+x<=7 and c1+y <=7 and r1+x>=0 and c1+y>=0):
                if(self.board[r1+x][c1+y]=='--'):
                    moves.append(Move((r,c),(r1+x,c1+y),self.board))
                else:
                    if(self.board[r1+x][c1+y][0]=='b' and self.whiteToMove) or (self.board[r1+x][c1+y][0]=='w' and not self.whiteToMove):
                        moves.append(Move((r,c),(r1+x,c1+y),self.board))
                    break
                r1 = r1+x
                c1 = c1+y  

    def getKingMoves(self,r,c,moves):
        dir = {(0,1),(1,0),(0,-1),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)}

        for (x,y) in dir:
            r1 = r
            c1 = c
            if(r1+x<=7 and c1+y <=7 and r1+x>=0 and c1+y>=0):
                if(self.board[r1+x][c1+y]=='--'):
                    moves.append(Move((r,c),(r1+x,c1+y),self.board))
                else:
                    if(self.board[r1+x][c1+y][0]=='b' and self.whiteToMove) or (self.board[r1+x][c1+y][0]=='w' and not self.whiteToMove):
                        moves.append(Move((r,c),(r1+x,c1+y),self.board))
                r1 = r1+x
                c1 = c1+y        

    def getKnightMoves(self,r,c,moves):
        dir = {(-1,-2),(-1,2),(1,-2),(1,2),(2,1),(2,-1),(-2,1),(-2,-1)}

        for (x,y) in dir:
            r1 = r
            c1 = c
            while(r1+x<=7 and c1+y <=7 and r1+x>=0 and c1+y>=0):
                if(self.board[r1+x][c1+y]=='--'):
                    moves.append(Move((r,c),(r1+x,c1+y),self.board))
                else:
                    if(self.board[r1+x][c1+y][0]=='b' and self.whiteToMove) or (self.board[r1+x][c1+y][0]=='w' and not self.whiteToMove):
                        moves.append(Move((r,c),(r1+x,c1+y),self.board))
                    break
                r1 = r1+x
                c1 = c1+y  

class Move():

    # creating a map to store mapping of index to original representation in the chess board (a-h,1-8)
    ranksToRows = {"1":7,"2":6,"3":5,"4":4,"5":3,"6":2,"7":1,"8":0}
    ranksToRows = { v:k for k,v in ranksToRows.items()}
    filesToCol  = {"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}
    filesToCol  = { v:k for k,v in filesToCol.items()}


    def __init__(self,startSq,endSq,board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol

    def __eq__(self,other):
        if isinstance(other,Move):
            return self.moveID == other.moveID
        return False
        


    def getChessNotations(self):
        return self.getRankFile(self.startRow,self.startCol)+self.getRankFile(self.endRow,self.endCol)

    def getRankFile(self,r,c):
        return self.filesToCol[c]+self.ranksToRows[r]


