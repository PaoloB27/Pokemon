# Author
Paolo Bresolin, AIDA Lab, Department of Information Engineering, University of Padova.

# Setup

Python version `3.12.3` is used for this project.
Only standard packages are used, so there is no need to install additional packages.

# Introduction

This project contains the implementation of a more complete pokemon game, where the user selects a starter pokemon and then can decide among the following actions:
- explore the pokemon world, where it can find a random wild pokemon with a fixed probability and fight against it;
- go to the pokemon center so to restore the HPs and PPs of all the trainer's pokemon;
- go to the pokemon store so to buy pokeballs and potions;
- exit the game.

# Files

In what follows, the content of each file present in the project will be briefly explained:
- `utils.py`: file with a few base functions regarding interactivity with the user and output printing;
- `pokemon_character.py`: contains the class `PokemonCharacter`, which represents a pokemon in the game;
- `pokemon_trainer.py`: contains the class `PokemonTrainer`, which represents a pokemon trainer in the game;
- `pokemons.py`: file with the three starter pokemons and and three wild pokemons;
- `pokemon moves.py`: file with the moves of the pokemons;
- `game_engine.py`: contains the definition of the class `GameEngine`, with the core functionalitis for running a game;
- `main.py`: main file used to run a game.

# Execution

To start a game, simply run the following command and follow the instructions printed in the standard output:
```
python main.py
```