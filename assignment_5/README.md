# Author
Paolo Bresolin, AIDA Lab, Department of Information Engineering, University of Padova.

# Setup

Python version `3.12.3` is used for this project.
The python packages necessary for this project along with theri versions are provided in the file `requirements.txt`.
To install them, run the following command:
```
pip install -r requirements.txt
```

# Introduction

This project contains the implementation of:
- a simulation that automatically runs an input number of games and an input number of random battles among pokemons chosen uniformly at random from the dataset, collecting data;
- the definition, training and validation of a Machine Learning (ML) model trained on simulation data to predict the outcome of a battle, given as input the active statistics and the types of the pokemons involved;
- the implementation of a more complete pokemon game. In particular, the most important new features with respect to the previous assignments are:
    - all pokemons are assigned an initial level that upgrades based on the outcomes of the battles they take part in;
    - the user can save the current game and load an existing one as well as start a new game;
    - the trained ML model is used as basis of a recommendation system that helps the user in the game by suggesting the most appropriate pokemon in the trainer's list at the beginning of each battle.

# Files

In what follows, the content of each file present in the project will be briefly explained.
Three directories are provided:
- `src`: directory that contains the implemented code. The files in `src` are:
    - `pokemon_character.py`: contains the class `PokemonCharacter`, which represents a pokemon;
    - `pokemon_trainer.py`: contains the class `PokemonTrainer`, which represents a pokemon trainer;
    - `simulation.py`: contains the definition of the class `Simulation`, with the core functionalitis for running a simulation to collect data for training the ML model;
    - `run_simulation.py`: script used to run a simulation;
    - `train_model.py`: script used to train a Random Forest on a training set extracted from the data collected with the simulation. The indices of samples not used for training are saved so to allow for evaluation on an unseed test set. A random search is performed for tuning the hyper parameters of the predictor. Then, a model instance on the whole training set is trained with the best found hyper parameters and the model is saved;
    - `evaluate_model.py`: evaluates the trained model on unseen data, printing some statistics and making some plots;
    - `utils.py`: file with a few base functions regarding interactivity with the user and output printing;
    - `game_engine.py`: contains the definition of the class `GameEngine`, with the core functionalitis for running a game;
    - `play.py`: main file used to run a game.
- `data`: directory with all data to run the simulation. In particular:
    - `moves.json`: file with all the moves that can be used by pokemons;
    - `pokemons.json`: file with all the possible pokemons that can be used;
    - `type_effectiveness.json`: file with all the pairs of types with a value that indicates the effectiveness of a move of a certain type against a  pokemon of another type;
- `results`: directory that contains some plots used to evaluate the performances of the trained model on unseen simulation data.
The file `collected_data.csv` has the data collected by a simulation run with standard parameters.

In addition, the file `requirements.txt` is present and reports all the packages used in the project with their versions.

# Execution

To run a simulation, run the following command:
```
python run_simulation.py
```

To train a recommender instance, run:
```
python train_model.py
```

To evaluate a trained model on an unseed test data, run the command:
```
python evaluate_model.py
```

To run the game with a trained model, run:
```
python play.py
```

All scripts have parameters that can be set by the user.
To have a detailed list of parameters for a script, run it with the flag `-h`.