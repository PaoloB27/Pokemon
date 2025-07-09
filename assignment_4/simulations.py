import os
import json
import pickle
from copy import deepcopy
import random
import argparse
import pandas as pd
from tqdm import tqdm
from pokemon_character import PokemonCharacter

def pokemon_from_dict(pokemon_dict):
    """
    Initializes a PokemonCharacter object from an input dictionary with its information.

    Parameters:
    - pokemon_dict: dictionary that must have the following entries:
                    - name: string with the name of the pokemon;
                    - baseStast: dictionary with the basic statistics of the pokemon;
                    - moves: list of dictionaries representing the moves of the pokemon;
                    - national_pokedex_number: integer resperenting the national pokedex number of the pokemon;
                    - types: list of strings with the types of the pokemon.
    
    Returns:
    - pokemon: PokemonCharacter initialized with the input information.
    """

    # initialize a PokemonCharacter with the input information
    pokemon = PokemonCharacter(
        name=pokemon_dict["name"],
        national_pokedex_number=pokemon_dict["national_pokedex_number"],
        types=pokemon_dict["types"],
        base_stats=pokemon_dict["baseStats"],
        moves=pokemon_dict["moves"]
    )

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
    return 

def load_pokemon(path, moves):
    """
    Loads a dataset of pokemons from a .json file.
    It adds the entry with key "level" and value 1 to each dictionary representing a pokemon.
    It also adds two moves to each pokemon by sampling them at random from the input moves such that type coherence is respected.

    Parameters:
    - path: path to the .json file with the pokemons to be loaded.

    Returns:
    - pokemons: dictionary of dictionaries with each dictionary that represents a different pokemon.
    """

    # initialize the dictionary that will contain the loaded pokemons
    pokemons = {}

    # open the .json file
    with open(path, "r") as file:
        
        # iterate through lines
        for line in file:

            # convert the line into a dictionary representing a pokemon
            curr_pokemon = json.loads(line)

            # add the entry ("level", 1)
            curr_pokemon["level"] = 1

            # add to the loaded pokemon 4 moves sampled uniformly at random from the input moves that have the same types of the current pokemon or of type "normal"
            curr_pokemon["moves"] = random.sample([move for move in moves.values() if move["type"] in curr_pokemon["types"] or move["type"] == "normal"], 4)
            
            # convert the current pokemon into a PokemonCharacter object and add it to the dictionary of pokemons
            pokemons[curr_pokemon["name"]] = pokemon_from_dict(curr_pokemon)

    return pokemons

def load_type_effectiveness(path):
    """
    Loads type effectiveness relations from a .json file.

    Parameters:
    - path: path to the .json file with the data to be loaded.

    Returns:
    - data: dictionary with the input data.
            Given an attack type "a" and a defend type "d", the effectiveness value is data["a"]["b"].
    """

    # initialize the dictionary that will contain the loaded data
    data = {}

    # open the .json file
    with open(path, "r") as file:
        
        # iterate through lines
        for line in file:

            # convert the line into a dictionary
            pair = json.loads(line)

            # add the pair to the dictionary
            if pair["attack"] in data:
                data[pair["attack"]][pair["defend"]] = pair["effectiveness"]
            else:
                data[pair["attack"]] = {pair["defend"]: pair["effectiveness"]}

    return data

def random_battle(input_pokemon, wild_pokemons, type_effectiveness):
    """
    A wild pokemon is sampled uniformly at random among the list of wild pokemons provided as input.
    Once that a wild pokemon is sampled, a battle between the trainer's starter pokemon and the sampled wild pokemon is run.
    The battle is led randomly by sampling uniformly at random a move at each turn for each of the two pokemons involved.

    Parameters:
    - input_pokemon: PokemonCharacter object representing the pokemon that has to fight against a wild pokemon.
    - wild_pokemons: list of dictionaries representing the wild pokemons that can be encountered.
    - type_effectiveness: dictionary with the effectivenesses of moves given the move type "move_type" and the defender pokemon's types.
                          type_effectiveness["move_type"]["defender_type"] is the float representing the effectiveness.

    Returns:
    - wild_pokemon_name: string with the name of the sampled wild pokemon to fight against the input pokemon.
    - battle_outcome: boolean indicating whether the battle is won by the input pokemon or not.
    - n_turns: integer with the total number of turns in the battle.
    - residual_HP_percentage: float with the percentage of residual HP of the input pokemon after the battle.
    """
        
    # sample uniformly at random a wild pokemon among the input ones, making a copy so to keep modifications only in the current battle
    sampled_pokemon = deepcopy(wild_pokemons[random.choice(list(wild_pokemons.keys()))])

    # initialize the number of turns of the battle
    n_turns = 1

    # start the battle and end it when one of the two pokemons has been defeated
    while True:
        
        # make the input pokemon attack the wild pokemon with a move chosen uniformly at random among those available
        input_pokemon.use_move(random.choice([move["name"] for move in input_pokemon.moves]), sampled_pokemon, type_effectiveness)

        # check whether the wild pokemon is defeated and end the battle in this case
        if sampled_pokemon.curr_hp <= 0:
            return sampled_pokemon.name, True, n_turns, input_pokemon.curr_hp / input_pokemon.base_stats["hp"] * 100
        
        # make the wild pokemon attack the input pokemon with a move sampled uniformly at random among the available ones
        sampled_pokemon.use_move(random.choice([move["name"] for move in sampled_pokemon.moves]), input_pokemon, type_effectiveness)
    
        # check whether the input pokemon is defeated and end the battle in this case
        if input_pokemon.curr_hp <= 0:
            return sampled_pokemon.name, False, n_turns, 0

        # update the number of turns
        n_turns += 1

def run_simulation(n_games, n_battles, starter_pokemons, wild_pokemons, type_effectiveness):
    """
    Simulates n_battles with the input starter pokemon against randomly sampled wild pokemons.
    After each battle, the trainer goes to the pokemon center.
    After that n_battles with the input starter pokemon have been completed, the game ends.

    Parameters:
    - n_games: integer representing the number of games to run for each input starter pokemon.
    - n_battles: integer representing the number of battles to be performed in each single game.
    - starter_pokemons: list of PokemonCharacter objects with the starter pokemons that have to be used.
    - wild_pokemons: dictionary with the wild pokemons.
    - type_effectiveness: dictionary with the effectiveness of a move given its type and the types of the opponent pokemon.

    Returns:
    - collected_data: list of dictionaries with all data collected in the simulation.
                      Each dictionary stores data for a given battle in a given game of a given starter pokemon.
    """

    # list that will contain all useful information across all battleas in all games and for all starter pokemons
    collected_data = []

    # run n_games games for each input starter pokemon
    for starter in starter_pokemons:

        # run n_games games
        for j in tqdm(range(1, n_games + 1), desc=f"Simulation {starter.name}", unit="game"):

            # run n_battles battles before exiting the game
            for k in range(1, n_battles + 1):

                # run the battle and append the collected data
                wild_pokemon_name, outcome, n_turns, residual_HP = random_battle(starter, wild_pokemons, type_effectiveness)
                collected_data.append(
                    {
                        "Starter Pokemon": starter.name,
                        "Wild Pokemon": wild_pokemon_name,
                        "Battle Outcome": outcome,
                        "Battle Turns": n_turns,
                        "Residual HP": residual_HP,
                        "Battle": k,
                        "Game": j
                    }
                )

                # make the trainer go to the pokemon center to heal the starter pokemon after the battle
                starter.curr_hp = starter.base_stats["hp"]

    return collected_data

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
    parser.add_argument("--output_data", type=str, required=False, default=os.path.join("results", "collected_data.pickle"), help="Path to the file where to save the collected data.")
                          
    return parser.parse_args()

if __name__ == '__main__':

    # parse command line arguments
    args = parse_args()

    # load pokemons, moves and type effectiveness data from .json files
    moves = load_moves(args.input_moves)
    pokemons = load_pokemon(args.input_pokemons, moves)
    type_effectiveness = load_type_effectiveness(args.input_type_effectiveness)

    # starter pokemons
    starter_pokemons = [p for p in pokemons.values() if p.name in ["bulbasaur", "charmander", "squirtle", "pikachu"]]

    # run the simulation
    collected_data = run_simulation(args.n_games, args.n_battles, starter_pokemons, pokemons, type_effectiveness)

    # save the collected data
    os.makedirs(os.path.dirname(args.output_data), exist_ok=True)
    pickle_out = open(args.output_data, "wb")
    pickle.dump(collected_data, pickle_out)
    pickle_out.close()
