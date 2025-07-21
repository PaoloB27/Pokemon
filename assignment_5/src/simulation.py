import os
from copy import deepcopy
import random
import pandas as pd
from tqdm import tqdm
from game_engine import GameEngine

class Simulation:

    def __init__(self, n_games, n_battles, pokemons_path, moves_path, type_effectiveness_path):
        """
        Initializes a simualtion with the input data.

        Parameters:
        - n_games: integer representing the number of games to run for each input starter pokemon.
        - n_battles: integer representing the number of battles to be performed in each single game.
        - pokemons_path: path to the .json file with the pokemons to be loaded.
        - moves_path: path to the .json file with the moves to be loaded.
        - type_effectiveness_path: path to the .json file with the type effectiveness data to be loaded.
        """

        # set the number of games
        self.n_games = n_games

        # set the number of battles
        self.n_battles = n_battles

        # load moves, pokemons and type effectiveness
        self.moves = GameEngine.load_moves(moves_path)
        self.pokemons = GameEngine.load_pokemons(pokemons_path, self.moves)
        self.type_effectiveness = GameEngine.load_type_effectiveness(type_effectiveness_path)

        # initialize the list that will contain data from the simulation run
        self.collected_data = []

    def random_battle(self, input_pokemon):
        """
        A wild pokemon is sampled uniformly at random.
        Once that a wild pokemon is sampled, a battle between the trainer's starter pokemon and the sampled wild pokemon is run.
        The battle is led randomly by sampling uniformly at random a move at each turn for each of the two pokemons involved.

        Parameters:
        - input_pokemon: PokemonCharacter object representing the pokemon that has to fight against a wild pokemon.

        Returns:
        - sampled_pokemon.active_stats: dictionary with the active stats of the sampled wild pokemon.
        - sampled_pokemon.types: list of strings representing the types of the sampled wild pokemon.
        - battle_outcome: integer indicating whether the battle has been won by the player (1) or not (0).
        """
            
        # sample uniformly at random a wild pokemon and a level in [1, 20], making a copy so to keep modifications only in the current battle
        sampled_pokemon = deepcopy(self.pokemons.sample(random_state=random.randint(0, 10000)).iloc[0])
        sampled_pokemon["level"] = random.randint(1, 20)
        sampled_pokemon = GameEngine.to_pokemon_character(sampled_pokemon)

        # start the battle and end it when one of the two pokemons has been defeated
        while True:
            
            # make the input pokemon attack the wild pokemon with a move chosen uniformly at random
            chosen_move = random.choice([move["name"] for move in input_pokemon.moves])
            input_pokemon.use_move(chosen_move, sampled_pokemon, self.type_effectiveness, verbose=False)

            # check whether the wild pokemon is defeated and end the battle in this case
            if sampled_pokemon.curr_hp <= 0:
                return sampled_pokemon.active_stats, sampled_pokemon.types, 1
            
            # make the wild pokemon attack the input pokemon with a move sampled uniformly at random
            chosen_move = random.choice([move["name"] for move in sampled_pokemon.moves])
            sampled_pokemon.use_move(chosen_move, input_pokemon, self.type_effectiveness, verbose=False)
        
            # check whether the input pokemon is defeated and end the battle in this case
            if input_pokemon.curr_hp <= 0:
                return sampled_pokemon.active_stats, sampled_pokemon.types, 0

    def run_simulation(self):
        """
        Simulates self.n_battles battles for each of self.n_games games against randomly sampled wild pokemons.
        At the beginning of each battle, a starter pokemon is selected uniformly at random among all the pokemons.
        The starter pokemon selected at the beginning of the game takes part in all the self.n_battles battles of the game.
        After each battle, the trainer goes to the pokemon center.
        After that self.n_battles have been completed, the game ends.
        """

        # initialize the data collected by this simulation as an empty list
        self.collected_data = []

        # run self.n_games games
        for j in tqdm(range(1, self.n_games + 1), desc=f"Running the Simulation", unit="game"):

            # run self.n_battles battles before exiting the game
            for k in range(1, self.n_battles + 1):

                # sample uniformly at random a starter pokemon and set its level to a random value in [1, 20]
                starter = self.pokemons.sample(random_state=random.randint(0, 10000)).iloc[0]
                starter["level"] = random.randint(1, 20)
                starter = GameEngine.to_pokemon_character(starter)

                # run the battle and collect data
                wild_act_stats, wild_types, battle_outcome = self.random_battle(starter)

                # add the data collected during the battle to the dictionary with all data
                curr_dict = {f"player_{stat_name}": stat_value for stat_name, stat_value in starter.active_stats.items()}
                curr_dict["player_types"] = starter.types
                for stat_name, stat_val in wild_act_stats.items():
                    curr_dict[f"opponent_{stat_name}"] = stat_val
                curr_dict["opponent_types"] = wild_types
                curr_dict["game"] = j
                curr_dict["battle"] = k
                curr_dict["outcome"] = battle_outcome
                self.collected_data.append(curr_dict)

                # make the trainer go to the pokemon center to heal the starter pokemon after the battle
                starter.curr_hp = starter.active_stats["hp"]

        self.collected_data = pd.DataFrame(self.collected_data)

    def save_data(self, output_path):
        """
        Saves the data collected by running the simulation.

        Parameters:
        - output_path: path to the file where to save the data.
        """

        # save the collected data
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.collected_data.to_csv(output_path, index=False)
