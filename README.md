# AmiGo
ML reinforcement model for the game of Go
https://www.nature.com/articles/nature24270
[agz_unformatted_nature.pdf](https://github.com/user-attachments/files/19464913/agz_unformatted_nature.pdf)


# AlphaZero Go on 5×5 Board

## Overview
This project implements a simplified version of DeepMind's AlphaZero algorithm to play the game of Go on a 5×5 board. Leveraging reinforcement learning (RL) without any human data, the system learns to achieve superhuman performance through self-play and Monte Carlo Tree Search (MCTS).

Key features:
- Inspired by Google DeepMind’s AlphaZero, achieving superhuman strength in board games.
- Pure RL approach: no human games or expert data used.
- Configurable board size (default 5×5, easily adjustable).
- Endgame and win conditions are tweaked for simplicity.
- Pretrained model (`model_19.pt`) included for instant play.

## The Game of Go
Go is an ancient two-player strategy board game with simple rules but immense complexity:
1. **Board**: Traditional sizes are 19×19, 13×13, or 9×9; here we use 5×5 for faster training and experimentation.
2. **Stones**: Black and White alternate placing stones on empty intersections.
3. **Groups & Liberties**: Connected stones form a group; liberties are adjacent empty points. Groups without liberties are captured and removed.
4. **Objective**: Surround more territory (empty points) and capture opponent stones. In this simplified version, the winner is decided by stone count when no legal moves remain or a line of identical stones dominates.

Despite its simple rules, Go’s game-tree complexity on a 5×5 board is already on the order of 3.1×10⁶ possible positions; a 19×19 board has ~10¹⁷⁰ possibilities.

## Project Structure & Cells Explanation
The code is organized into Jupyter notebook cells; here’s what each cell does:

1. **Cell 1** (`GoGameAlphaZero`):
   - Implements the Go game logic on an N×N board.
   - Manages state representation, valid move generation, capturing rules, and endgame evaluation.

2. **Cell 2** (`ResNet` & `ResBlock`):
   - Defines the neural network architecture: a convolutional residual network for policy and value heads.
   - Takes a 3-channel encoded board state and outputs move probabilities and game-value predictions.

3. **Cell 3** (Demo & Visualization):
   - Shows how to instantiate the game, make moves, encode state, and run the `ResNet` forward pass.
   - Plots the policy distribution over the 25 actions using Matplotlib.

4. **Cell 4** (`Node` & `MCTS`):
   - Implements the MCTS logic with Upper Confidence Bound (UCB) for selection, expansion, simulation via the neural network, and backpropagation of values.

5. **Cell 5** (`AlphaZero` class):
   - Coordinates self-play, training, and evaluation loops.
   - Saves the best model based on win-rate improvement and checkpoints after each iteration.

6. **Cell 6** (Interactive Play Script):
   - Provides a command-line interface to play against the trained model.
   - Loads `model_19.pt` and uses MCTS for AI moves; allows human vs. AI games on the console.

## Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install torch numpy matplotlib tqdm
   ```
3. Place `model_19.pt` in the project root for immediate play.

## Usage
### Play with Pretrained Model
```bash
python play.py    # uses model_19.pt by default
```
Follow on-screen prompts to play as Black against the AI.

### Train from Scratch
1. Adjust parameters in `train.py` (e.g., board size, number of iterations).
2. Run:
   ```bash
   python train.py
   ```
3. New models and optimizers are saved per iteration. To use a newly trained model, place its `.pt` file in the root and run the play script.

## Configuration
- **Board Size**: Change `board_size` in `GoGameAlphaZero` initializer.
- **AlphaZero Arguments** (in code):
  - `C`: Exploration constant for UCB.
  - `num_searches`: MCTS rollouts per move.
  - `num_iterations`: Meta-iterations of self-play + training.
  - `num_selfPlay_iterations`: Games per iteration.
  - `num_epochs`: Training epochs per iteration.
  - `batch_size`: Samples per training batch.
  - `evaluation_games`: Games to evaluate win rate.

## Contributing
Feel free to:
- Scale to larger board sizes.
- Experiment with network depth/width.
- Integrate with GPU training.

## License
This project is released under the MIT License. Enjoy exploring AlphaZero on small boards!

