
# Chess Engine

Hey everyone, I have implemented a chess engine in python using the pygame module.

# Journey

I have firstly implemented the chess game with functionality so that we can determine the possible moves and then set the conditions for each of the piece to determine which all moves are valid ones, also added the feature of king castling, pawn en passant.

Now at this stage our chess game was ready and two players can comfortably play with all safety measures such that no one can make a faulty move.

Then I tried to implement the Computer or as I referred as ChessAI which may play against you and choose the optimal move at every instance of time.

I did start with Ai generating random moves then I moved on to greedy algorithm where AI chooses the moves from the validMoves list and then move 1 stage ahead to check if it will lead to more beneficial result and if I used the best greedy move. 

Now My ChessAI was playing with me, my curiosity made me to think what if we can check for two stages the best optimal move possible and use that result, it will be much more efficient. So I then used the MinMax algorithm to implement two stage based ChessAi.(Stage here is referred to depth)

Then I switched my algorithm from MinMax to NegaMax which can referred as the recursive implementation of MinMax algorithm, just that we can choose whatever depth we want to look for. 

Now I was ready with with a very effiecient algorithm which chooses nice move but it was quite slow for the depth of 2 and more.

To make it faster, I used the concept of alpha beta pruning which made my program preety faster than the previous one. 

So, This is the progress of my project till now. I did look for different algortihm available like hashing technique which used the Material sum and material difference which player is in advantage but they were less efficient than the one I used in which I assigned each piece a particular score and also assigned particular score to board for every position of every piece.


## Requirements

As this project uses pygame module, so we need to install this,
```bash 
pip install pygame

