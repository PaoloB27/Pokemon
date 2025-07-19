import os
import json
import pickle
from copy import deepcopy
import random
from tqdm import tqdm
from pokemon_character import PokemonCharacter

class Simulation:

    def __init__(self, n_games, n_battles, pokemons_path, moves_path, type_effectiveness_path, starter_pokemons=["bulbasaur", "charmander", "squirtle", "pikachu"]):
        """
        Initializes a simualtion with the input data.

        Parameters:
        - n_games: integer representing the number of games to run for each input starter pokemon.
        - n_battles: integer representing the number of battles to be performed in each single game.
        - pokemons_path: path to the .json file with the pokemons to be loaded.
        - moves_path: path to the .json file with the moves to be loaded.
        - type_effectiveness_path: path to the .json file with the type effectiveness data to be loaded.
        - starter_pokemons: list of strings with the names of the starter pokemons to be used in the simulation.
        """

        # set the number of games
        self.n_games = n_games

        # set the number of battles
        self.n_battles = n_battles

        # load moves, pokemons and type effectiveness
        self.moves = self.load_moves(moves_path)
        self.pokemons = self.load_pokemons(pokemons_path, self.moves)
        self.type_effectiveness = self.load_type_effectiveness(type_effectiveness_path)

        # set the names of the starter pokemons
        self.starter_names = starter_pokemons

        # initialize the list that will contain data from the simulation run
        self.collected_data = []

    @staticmethod
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

    @staticmethod
    def load_moves(path):
        """
        Loads a dataset of moves from a .json file.
        It removes the moves with "power" equal to null and the keys "effect", "effects", "changes".

        Parameters:
        - path: path to the .json file with the moves to be loaded.

        Returns:
        - moves: dictionary of dictionaries with each entry that is a different move.
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

                # add the move only if the value of "power" and "accuracy" are not None
                if move["power"] is not None and move["accuracy"] is not None:
                    
                    # consider the name as key and all information as value, but remove the entries with key in keys_to_remove
                    moves[move["name"]] = {key: value for key, value in move.items() if key not in keys_to_remove}

        return moves

    @staticmethod
    def load_pokemons(path, moves):
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
                pokemons[curr_pokemon["name"]] = Simulation.pokemon_from_dict(curr_pokemon)

        return pokemons

    @staticmethod
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

    def random_battle(self, input_pokemon):
        """
        A wild pokemon is sampled uniformly at random among the list of wild pokemons provided as input.
        Once that a wild pokemon is sampled, a battle between the trainer's starter pokemon and the sampled wild pokemon is run.
        The battle is led randomly by sampling uniformly at random a move at each turn for each of the two pokemons involved.

        Parameters:
        - input_pokemon: PokemonCharacter object representing the pokemon that has to fight against a wild pokemon.

        Returns:
        - wild_pokemon_name: string with the name of the sampled wild pokemon to fight against the input pokemon.
        - battle_outcome: boolean indicating whether the battle is won by the input pokemon or not.
        - n_turns: integer with the total number of turns in the battle.
        - residual_HP_percentage: float with the percentage of residual HP of the input pokemon after the battle.
        """
            
        # sample uniformly at random a wild pokemon among the input ones, making a copy so to keep modifications only in the current battle
        sampled_pokemon = deepcopy(self.pokemons[random.choice(list(self.pokemons.keys()))])

        # initialize the number of turns of the battle
        n_turns = 1

        # start the battle and end it when one of the two pokemons has been defeated
        while True:
            
            # make the input pokemon attack the wild pokemon with a move chosen uniformly at random among those available
            input_pokemon.use_move(random.choice([move["name"] for move in input_pokemon.moves]), sampled_pokemon, self.type_effectiveness)

            # check whether the wild pokemon is defeated and end the battle in this case
            if sampled_pokemon.curr_hp <= 0:
                return sampled_pokemon.name, True, n_turns, input_pokemon.curr_hp / input_pokemon.base_stats["hp"] * 100
            
            # make the wild pokemon attack the input pokemon with a move sampled uniformly at random among the available ones
            sampled_pokemon.use_move(random.choice([move["name"] for move in sampled_pokemon.moves]), input_pokemon, self.type_effectiveness)
        
            # check whether the input pokemon is defeated and end the battle in this case
            if input_pokemon.curr_hp <= 0:
                return sampled_pokemon.name, False, n_turns, 0

            # update the number of turns
            n_turns += 1

    def run_simulation(self):
        """
        Simulates self.n_battles with the input starter pokemon against randomly sampled wild pokemons.
        After each battle, the trainer goes to the pokemon center.
        After that self.n_battles with the input starter pokemon have been completed, the game ends.
        """

        # extract the starter pokemons
        starter_pokemons = [pokemon for pokemon in self.pokemons.values() if pokemon.name in self.starter_names]

        # run n_games games for each input starter pokemon
        for starter in starter_pokemons:

            # run n_games games
            for j in tqdm(range(1, self.n_games + 1), desc=f"Simulation {starter.name}", unit="game"):

                # run n_battles battles before exiting the game
                for k in range(1, self.n_battles + 1):

                    # run the battle and append the collected data
                    wild_pokemon_name, outcome, n_turns, residual_HP = self.random_battle(starter)
                    self.collected_data.append(
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

    def save_data(self, output_path):
        """
        Saves the collected data to the input .pickle file.

        Parameters:
        - output_path: path to the .pickle file where to save the collected data.
        """

        # save the data collected by the simulation
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pickle_out = open(output_path, "wb")
        pickle.dump(self.collected_data, pickle_out)
        pickle_out.close()