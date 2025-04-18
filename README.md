# Pokeguess

Pokeguess is a Pokémon guessing game inspired by pokedle.com. The player must guess a randomly selected Pokémon from Gens 1 and 2. After each guess, the game provides feedback on various attributes using colored backgrounds:

- **Green:** exact match
- **Yellow:** partial match (for multi-valued attributes)
- **Red:** no match

## Features

- Modern graphical user interface with color-coded feedback
- Guess any of the first 251 Pokémon by name (case-insensitive)
- Progressive hint system that reveals one letter at a time
- Scrollable results area to accommodate multiple guesses
- Submit guesses using the Enter key or Submit button

### Compare attributes:
- Type 1 and Type 2
- Evolution stage (1–3)
- Fully evolved status (Yes/No)
- Colors (up to two)
- Habitats (one or more, comma-delimited)
- Generation (1)

The game tracks number of attempts and congratulates the player upon correct guess.

## Screenshots

[Screenshot placeholder - add screenshots of your game after pushing to GitHub]

## Requirements

- Python 3.6 or higher
- Tkinter (python3-tk)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/joeysurfs/pokeguess-game.git
   ```

2. Change into the project directory:
   ```
   cd pokeguess-game
   ```

3. Ensure that `pokemon_info.json` is present in the root of the project.

4. Install Tkinter if not already installed:
   ```
   # For Ubuntu/Debian
   sudo apt-get install python3-tk
   
   # For Fedora
   sudo dnf install python3-tkinter
   
   # For macOS (if using Homebrew)
   brew install python-tk
   ```

## Usage

Run the game with:

```
python main.py
```

The GUI will launch, allowing you to:
1. Enter Pokémon names in the input field
2. Use the "Get Hint" button for progressive hints about the target Pokémon
3. See color-coded feedback for each of your guesses
4. Reset the game at any time

## Project Structure

```
pokedle-game/
├── main.py           # Game logic and GUI interface
├── pokemon_info.json # Data for Pokémon
└── README.md         # This file
```
