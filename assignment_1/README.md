# Author
Paolo Bresolin, AIDA Lab, Department of Information Engineering, University of Padova.

# Setup

Python version `3.12.3` is used for this project.
Only standard packages are used, so there is no need to install additional packages.

# Introduction

This project contains the implementation of a simple pokemon game, where the user selects a starter pokemon and then leads a battle against a random starter pokemon.
The game finishes when the battle ends.

# Files

In what follows, the content of each file present in the project will be briefly explained:
- `utils.py`: file with a few base functions regarding interactivity with the user and output printing;
- `pokemon_character.py`: contains the class `PokemonCharacter`, which represents a pokemon in the game;
- `pokemon_trainer.py`: contains the class `PokemonTrainer`, which represents a pokemon trainer in the game;
- `pokemons_and_moves.py`: file with data, including both the three starter pokemons and the moves that they can use;
- `simple_game.py`: contains the definition of the class `SimpleGame`, with the core functionalitis for running a game;
- `main.py`: main file used to run a game.

# Execution

To start the game, simply run the following command and follow the instructions printed in the standard output:
```
python main.py
```