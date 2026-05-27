# Angry Birds (2-Player Pygame Clone)

A 2-player local multiplayer clone of Angry Birds built in Python using Pygame. Players enter their names, choose their birds, select a level, toggle the wind conditions, and compete to get the highest score by destroying obstacles!

## Features

- **2-Player Local Multiplayer**: Turn-based action where Player 1 and Player 2 compete.
- **Multiple Bird Types**: Choose from Red, Chuck, Bomb, and Blue birds, each having different properties.
- **3 Playable Levels**: Different configurations of wood, ice, and stone obstacles.
- **Wind System**: Turn on "Wind Impulse" to add dynamic wind forces that affect the bird's trajectory during flight.
- **Sound Effects**: Retro SFX for launching, victory, and bird selection.
- **Scoreboard & High Scores**: Tracking of individual player scores and local high scores.

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (fast Python package manager)

## Setup and Running

1. **Install dependencies and run the game** using `uv`:
   ```bash
   uv run main.py
   ```

## How to Play

1. **Enter Names**: Player 1 and Player 2 enter their names in the starting screen. Press `Enter` after typing each name.
2. **Choose Birds**: Select your bird by clicking on one of the available choices (Red, Chuck, Bomb, Blue).
3. **Choose Level**: Choose from Level 1, Level 2, or Level 3.
4. **Wind State**: Enable or disable the wind impulse feature.
5. **Aim & Launch**: Click and drag back on the bird inside the slingshot to aim (a trajectory preview arc will be shown). Release the mouse button to launch the bird.
6. **Goal**: Destroy all obstacles on the screen before the timer runs out!
