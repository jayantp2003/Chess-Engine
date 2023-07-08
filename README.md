# Chess Engine Project

This project aims to develop a chess engine in Python, utilizing Pygame library, that incorporates various functionalities and intelligent algorithms to enhance move selection and provide an optimized playing experience.

## Project Features

- Engine development in Python using Pygame to implement key chess functionalities such as En Passant, Promotion, Castling, and all possible moves.
- Integration of a Greedy Algorithm to predict the optimal move, enhancing move selection.
- Implementation of the MinMax algorithm to analyze moves two stages ahead, improving the ChessAI's decision-making capability.
- Further refinement with the implementation of the NegaMax algorithm, a recursive version of MinMax, allowing customizable depth for move analysis.

## Project Progression

1. The chess game was initially implemented, providing functionality to determine possible moves and setting conditions for valid moves, including features like king castling and pawn en passant.

2. With the completion of the chess game, two players can comfortably play with safety measures to prevent faulty moves.

3. The implementation of the ChessAI, which plays against human players, began with generating random moves.

4. The AI's move selection was then improved by incorporating the Greedy Algorithm, selecting moves from the validMoves list and considering their potential benefits by analyzing the subsequent move.

5. To enhance efficiency, the MinMax algorithm was employed to enable two-stage based move analysis, resulting in better move selection.

6. The algorithm was further refined by switching to the NegaMax implementation, offering flexibility in selecting the desired depth for move analysis.

7. While the NegaMax algorithm proved efficient, it became slower for depths of 2 and beyond. To address this, the concept of alpha-beta pruning was utilized, significantly improving the program's speed.

8. Various algorithms, including hashing techniques based on material sums and differences, were explored. However, the scoring approach, assigning specific scores to each piece and evaluating the board for each position, proved to be more efficient.

# Requirements

As this project uses pygame module, so we need to install this,
```bash 
pip install pygame
```
# Usage

1. Clone the repo into your local directory.
```
git clone https://github.com/jayantp2003/Chess-Engine.git
```   
2. Install the requirement
```
pip install pygame
```
3. Move into chess directory
```
cd chess
```
Note : In the Main file, we have the option of player 1 and player 2 where we can decide which one is for AI and which one is for human. You are allowed to play all four possible combination of human and AI.

4. Run ChessMain.py
```
python ChessMain.py
```

