import os
import json
from copy import deepcopy
import random
import argparse
import pandas as pd
from tqdm import tqdm
from pokemon_character import PokemonCharacter

def to_pokemon_character(row_df):
    """
    Converts the row of a dataframe with pokemon information into a PokemonCharacter object.

    Parameters:
    - row_df: row of a pandas dataframe with all information about a pokemon.

    Returns:
    - pokemon: PokemonCharacter with all information in the input row about a pokemon.
    """

    # instantiate a PokemonCharacter object with the input information
    pokemon = PokemonCharacter(
        name=row_df["name"],
        base_stats=row_df["baseStats"],
        moves=row_df["moves"],
        national_pokedex_number=row_df["national_pokedex_number"],
        types=row_df["types"],
        level=row_df["level"]
    )

    # return the PokemonCharacter object
    return pokemon

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

    # initialize the list of dictionaries that will contain the loaded moves
    moves = []

    # open the .json file
    with open(path, "r") as file:
        
        # iterate through lines
        for line in file:

            # convert the string into a dictionary
            move = json.loads(line)

            # add the move only if the value of "power" and "accuracy" are not None
            if move["power"] is not None and move["accuracy"] is not None:
                
                # remove the entries with key in keys_to_remove
                move = {key: value for key, value in move.items() if key not in keys_to_remove}

                # add the dictionary repesenting a move to the list
                moves.append(move)

    # return the loaded moves in a pandas dataframe
    return pd.DataFrame(moves)

def load_pokemons(path, moves):
    """
    Loads a dataset of pokemons from a .json file.
    It adds the entry with key "level" and value 1 to each dictionary representing a pokemon.
    It also adds two moves to each pokemon by sampling them at random from the input moves such that type coherence is respected.

    Parameters:
    - path: path to the .json file with the pokemons to be loaded.

    Returns:
    - pokemons: dataframe with each entry that represents a different pokemon.
    """

    # initialize the list that will contain the loaded pokemons
    pokemons = []

    # open the .json file
    with open(path, "r") as file:
        
        # iterate through lines
        for line in file:

            # convert the line into a dictionary representing a pokemon
            curr_pokemon = json.loads(line)

            # add the entry ("level", 1)
            curr_pokemon["level"] = 1

            # add to the loaded pokemon 4 moves sampled uniformly at random from the input moves that have the same types of the current pokemon or of type "normal"
            curr_pokemon["moves"] = moves[(moves["type"] == "normal") | (moves["type"].isin(curr_pokemon["types"]))].sample(n=4, random_state=random.randint(0, 10000)).to_dict(orient="records")
            
            # append the current pokemon to the list of pokemons
            pokemons.append(curr_pokemon)

    # return the loaded pokemons as a pandas dataframe
    return pd.DataFrame(pokemons)

def load_type_effectiveness(path):
    """
    Loads type effectiveness relations from a .json file.

    Parameters:
    - path: path to the .json file with the data to be loaded.

    Returns:
    - data: pandas dataframe with the input data. Each row is a different (attack_type, defend_type) pair.
    """

    # initialize the list that will contain the loaded data
    data = []

    # open the .json file
    with open(path, "r") as file:
        
        # iterate through lines
        for line in file:

            # convert the line into a dictionary
            pair = json.loads(line)

            # append the pair to the list
            data.append(pair)

    # return the loaded type effectivenesses after having converted them into a pandas dataframe
    return pd.DataFrame(data)

def random_battle(input_pokemon, wild_pokemons, type_effectiveness):
    """
    A wild pokemon is sampled uniformly at random among the list of wild pokemons provided as input.
    Once that a wild pokemon is sampled, a battle between the trainer's starter pokemon and the sampled wild pokemon is run.
    The battle is led randomly by sampling uniformly at random a move at each turn for each of the two pokemons involved.

    Parameters:
    - input_pokemon: PokemonCharacter object representing the pokemon that has to fight against a wild pokemon.
    - wild_pokemons: pandas dataframe representing the wild pokemons that can be encountered.
    - type_effectiveness: pandas dataframe with the effectivenesses of moves given the move type "move_type" and the defender pokemon's types.

    Returns:
    - wild_pokemon_name: string with the name of the sampled wild pokemon to fight against the input pokemon.
    - battle_outcome: integer with a binary value indicating whether the battle is won (1) by the input pokemon or not (0).
    - n_turns: integer with the total number of turns in the battle.
    - residual_HP_percentage: float with the percentage of residual HP of the input pokemon after the battle.
    - data_all_turns: list that contains the residual hps of the input pokemon, the attacks perfomed by both pokemons and the damage inflicted by both pokemons at each turn.
                      data_all_turns[i] is a dictionary with all information about turn i.
    """
        
    # sample uniformly at random a wild pokemon and a level in [1, 20], making a copy so to keep modifications only in the current battle
    sampled_pokemon = deepcopy(wild_pokemons.sample(random_state=random.randint(0, 10000)).iloc[0])
    sampled_pokemon["level"] = random.randint(1, 20)
    sampled_pokemon = to_pokemon_character(sampled_pokemon)

    # initialize the lists that will contain data for each turn
    data_all_turns = []

    # initialize the number of turns of the battle
    n_turns = 1

    # start the battle and end it when one of the two pokemons has been defeated
    while True:

        # add the turn number and the current hps of the input pokemon to dictionary with the information related to the current turn
        curr_turn_info = {"Turn": n_turns, "Starter Initial HPs": input_pokemon.curr_hp}
        
        # make the input pokemon attack the wild pokemon with a move chosen uniformly at random and add the information to the dictionary
        chosen_move = random.choice([move["name"] for move in input_pokemon.moves])
        curr_turn_info["Starter Move"] = chosen_move
        curr_turn_info["Starter Damage Inflicted"] = input_pokemon.use_move(chosen_move, sampled_pokemon, type_effectiveness)

        # check whether the wild pokemon is defeated and end the battle in this case
        if sampled_pokemon.curr_hp <= 0:
            curr_turn_info["Wild Move"] = None
            curr_turn_info["Wild Damage Inflicted"] = None
            data_all_turns.append(curr_turn_info)
            return sampled_pokemon.name, 1, n_turns, input_pokemon.curr_hp / input_pokemon.active_stats["hp"] * 100, data_all_turns
        
        # make the wild pokemon attack the input pokemon with a move sampled uniformly at random and add the information to the dictionary
        chosen_move = random.choice([move["name"] for move in sampled_pokemon.moves])
        curr_turn_info["Wild Move"] = chosen_move
        curr_turn_info["Wild Damage Inflicted"] = sampled_pokemon.use_move(chosen_move, input_pokemon, type_effectiveness)
        data_all_turns.append(curr_turn_info)
    
        # check whether the input pokemon is defeated and end the battle in this case
        if input_pokemon.curr_hp <= 0:
            return sampled_pokemon.name, 0, n_turns, 0, data_all_turns

        # update the number of turns
        n_turns += 1

def run_simulation(n_games, n_battles, starter_pokemons, wild_pokemons, type_effectiveness):
    """
    Simulates n_battles battles for each of n_games games against randomly sampled wild pokemons.
    At the beginning of each battle, a starter pokemon is selected uniformly at random among the input ones.
    The starter pokemon selected at the beginning of the game takes part in all the n_battles battles of the game.
    After each battle, the trainer goes to the pokemon center.
    After that n_battles have been completed, the game ends.

    Parameters:
    - n_games: integer representing the number of games to run.
    - n_battles: integer representing the number of battles to be performed in each single game.
    - starter_pokemons: pandas Series of dictionaries with information about the starter pokemons that have to be considered.
    - wild_pokemons: pandas dataframe with the wild pokemons.
    - type_effectiveness: pandas dataframe with the effectiveness of a move given its type and the types of the opponent pokemon.

    Returns:
    - collected_data: pandas dataframe with all data collected in the simulation.
                      Each row stores information about a single turn of a battle in a game.
    """

    # list that will contain all useful information across all battles in all games
    collected_data = []

    # run n_games games
    for j in tqdm(range(1, n_games + 1), desc=f"Running the Simulation", unit="game"):

        # sample uniformly at random a starter pokemon and set its level to a random value in [1, 20]
        starter = starter_pokemons.sample(random_state=random.randint(0, 10000)).iloc[0]
        starter["level"] = random.randint(1, 20)
        starter = to_pokemon_character(starter)

        # run n_battles battles before exiting the game
        for k in range(1, n_battles + 1):

            # run the battle and collect data
            wild_pokemon_name, outcome, n_turns, residual_HP, turns_data = random_battle(starter, wild_pokemons, type_effectiveness, random_seed)

            # add the data related to the entire battle to each dictionary with information for a single turn
            for turn in turns_data:
                turn["Wild Pokemon"] = wild_pokemon_name
                turn["Starter Pokemon"] = starter.name
                turn["Battle Outcome"] = outcome
                turn["Battle Turns"] = n_turns
                turn["Residual HP"] = residual_HP
                turn["Battle"] = k
                turn["Game"] = j

            # extend the list with data for all turns battles with data for the current battle
            collected_data.extend(turns_data)

            # make the trainer go to the pokemon center to heal the starter pokemon after the battle
            starter.curr_hp = starter.active_stats["hp"]

    return pd.DataFrame(collected_data)

def parse_args():
    """
    Parses command line arguments.

    Returns:
    - parser.parse_args(): ArgumentParser object with parsed arguments.
    """

    # create the argument parser
    parser = argparse.ArgumentParser(description="Runs a simulation with random battles, collecting and saving data.")

    # arguments
    parser.add_argument("--n_games", type=int, required=False, default=1000, help="Number of games to run.")
    parser.add_argument("--n_battles", type=int, required=False, default=500, help="Number of battles to run in each game.")
    parser.add_argument("--input_pokemons", type=str, required=False, default=os.path.join("..", "data", "pokemons.json"), help="Path to the dataset with pokemons.")
    parser.add_argument("--input_moves", type=str, required=False, default=os.path.join("..", "data", "moves.json"), help="Path to the dataset with moves.")
    parser.add_argument("--input_type_effectiveness", type=str, required=False, default=os.path.join("..", "data", "type_effectiveness.json"), help="Path to the dataset with type effectiveness pairs.")
    parser.add_argument("--output_data", type=str, required=False, default=os.path.join("results", "collected_data.csv"), help="Path to the file where to save the collected data.")
    parser.add_argument("--random_seed", type=int, required=False, default=27, help="Random seed for reproducibility.")
                          
    return parser.parse_args()

if __name__ == '__main__':

    # parse command line arguments
    args = parse_args()

    # set a random seed for reproducibility
    random.seed(args.random_seed)

    # load pokemons, moves and type effectiveness data from .json files
    moves = load_moves(args.input_moves)
    pokemons = load_pokemons(args.input_pokemons, moves)
    type_effectiveness = load_type_effectiveness(args.input_type_effectiveness)

    # starter pokemons
    starter_pokemons = pokemons[pokemons["name"].isin(["bulbasaur", "charmander", "squirtle", "pikachu"])]

    # run the simulation
    collected_data = run_simulation(args.n_games, args.n_battles, starter_pokemons, pokemons, type_effectiveness, args.random_seed)

    # save the collected data
    os.makedirs(os.path.dirname(args.output_data), exist_ok=True)
    collected_data.to_csv(args.output_data, index=False)
