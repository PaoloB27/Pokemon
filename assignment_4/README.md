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

This project contains the implementation of a simulation that automatically runs an input number of games and an input number of battles, collecting data.
More precisely, `n_battles` battles are run for `n_games` games, leading to `n_battles * n_games` total battles.
At the beginning of each battle a starter pokemon is chosen uniformly at random among the input options and a wild pokemon is sampled uniformly at random among all possible pokemons in the game.

The collected data is then analyzed by another implemented script, which provides as output some results and saves interesting plots.

The main differences with respect to the simulation implemented in `../assignment_3/` lie in:
- the usage of Pandas DataFrames rather than Pickle objects to store data;
- the kind of data collected during a simulation run;
- the type of analysis performed, which results in different plots.

# Files

In what follows, the content of each file present in the project will be briefly explained.
Three directories are provided:
- `src`: directory that contains the implemented code. The files in `src` are:
    - `pokemon_character.py`: contains the class `PokemonCharacter`, which represents a pokemon in the game;
    - `simulation.py`: contains the definition of the class `Simulation`, with the core functionalitis for running a simulation;
    - `run_simulation.py`: script used to run a simulation;
    - `analize_data.py`: script used to analyze the data collected during a simulation run;
- `data`: directory with all data to run the simulation. In particular:
    - `moves.json`: file with all the moves that can be used by pokemons in the simulation;
    - `pokemons.json`: file with all the possible pokemons that can be used in the game;
    - `type_effectiveness.json`: file with all the pairs of types with a value that indicates the effectiveness of a move of a certain type against a  pokemon of another type;
- `results`: directory that contains some results obtained by the analysis of data provided by a simulation run with standard input parameters.
Inside, the file `collected_data.csv` has the data collected by a simulation run with standard parameters.

In addition, the file `requirements.txt` is present and reports all the packages used in the project with their versions.

# Execution

To run a simulation, run the following command:
```
python run_simulation.py
```

To analyze the data produced by a simulation, run:
```
python analize_data.py
```

Both the scripts have parameters that can be set by the user.
To have a detailed list of parameters for a script, run it with the flag `-h`.