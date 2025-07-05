import os
import json
import pandas as pd

def load_moves(path):
    """
    Loads a dataset of moves from a .json file.
    It removes the moves with "power" equal to null and the keys "effect", "effects", "changes".

    Parameters:
    - path: path to the .json file with the moves to be loaded.

    Returns:
    - moves: pandas dataframe with each entry that is a different move.
    """

    # keys to be removes
    keys_to_remove = ["effect", "effects", "changes"]

    # initialize the dictionary that will contain the loaded moves
    moves = {}

    # open the .json file
    with open(path, "r") as file:
        
        # iterate through lines
        for line in file:

            # convert the string into a dictionary
            move = json.loads(line)

            # add the move only if the value of "power" is not None
            if move["power"] is not None:
                
                # consider the name as key and all information as value, but remove the entries with key in keys_to_remove
                moves[move["name"]] = {key: value for key, value in move.items() if key not in keys_to_remove}

    return moves

def load_moves(path):
    """
    Loads a dataset of moves from a .json file.
    It removes the moves with "power" equal to null and the keys "effect", "effects", "changes".

    Parameters:
    - path: path to the .json file with the moves to be loaded.

    Returns:
    - moves: pandas dataframe with each entry that is a different move.
    """

    # keys to be removes
    keys_to_remove = ["effect", "effects", "changes"]

    # initialize the dictionary that will contain the loaded moves
    moves = {}

    # open the .json file
    with open(path, "r") as file:
        
        # iterate through lines
        for line in file:

            # convert the string into a dictionary
            move = json.loads(line)

            # add the move only if the value of "power" is not None
            if move["power"] is not None:
                
                # consider the name as key and all information as value, but remove the entries with key in keys_to_remove
                moves[move["name"]] = {key: value for key, value in move.items() if key not in keys_to_remove}

    return moves

def load_type_effectiveness(path):
    """
    Loads type effectiveness relations from a .json file.

    Parameters:
    - path: path to the .json file with the data to be loaded.

    Returns:
    - data: pandas dataframe with the input data. Each entry is a different pair of types.
    """

    # initialize the list that will contain the loaded data
    data = []

    # open the .json file and load the data by considering each line as a different entry
    with open(path, "r") as file:
        for line in file:
            data.appenf(json.loads(line))

    # return the data as a pandas dataframe
    return pd.DataFrame(data)

if __name__ == '__main__':
    
    # paths to the data to be loaded
    pokemon_path = os.path.join("..", "data", "pokemons.json")
    moves_path = os.path.join("..", "data", "moves.json")
    type_effectiveness_path = os.path.join("..", "data", "type_effectiveness.json")

    # load pokemon, moves and type effectiveness data from .json files
    moves = load_moves(moves_path)
    # pokemon = load_pokemon_or_moves(pokemon_path)
    # type_effectiveness = load_type_effectiveness(type_effectiveness_path)

    
