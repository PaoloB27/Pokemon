import random
import math
# from utils import type_text

class PokemonCharacter:
    """
    Class to represent a pokemon in the pokemon game.
    """

    def __init__(self, name, base_stats, moves, national_pokedex_number, types=["normal"], level=1):
        """
        A pokemon character is initialized by setting the parameters below.

        Parameters:
        - name: string with the name of the pokemon.
        - base_stats: dictionary with the base stats of the pokemon.
                      The dictionary must include:
                      - "hp": integer with the maximum health points of the pokemon.
                      - "attack": integer with the attack power of the pokemon.
                      - "defense": integer with the defense power of the pokemon.
                      - "speed": integer with the speed of the pokemon.
                      - "special": integer used to attack and defend with special moves.
        - moves: list of dictionaries containing a maximum of 4 moves that the pokemon can make during a battle.
                 Each doictionary must include:
                 - "name": string with the name of the move.
                 - "type": string with the type of the move.
                 - "category": string with the category of the move. It can be "physical" or "special".
                 - "power": integer with the power of the move.
                 - "accuracy": float representing the probability of hitting the opponent pokemon with the move.
                 - "pp": integer with the maximum number of times that the move can be used.
        - national_pokedex_number: integer with the national pokedex number of the pokemon.
        - types: list with the types of the pokemon. By default, the pokemon is of type "normal".
        - level: integer with the level of the pokemon. The default is 1, the minimum level a pokemon can have.
        """

        # name of the pokemon
        self.name = name

        # national pokedex number of the pokemon
        self.national_pokedex_number = national_pokedex_number

        # initialize the level of the pokemon
        self.level = level

        # set the types of the pokemon
        self.types = types

        # initialize the base stats of the pokemon
        self.base_stats = base_stats

        # initialize the current HP of the pokemon to the maximum
        self.curr_hp = self.base_stats["hp"]

        # set the moves of the pokemon
        self.moves = moves

        # initialize the PP of the moves to the maximum
        self.curr_pps = {}
        for move in self.moves:
            self.curr_pps[move["name"]] = move["pp"]
    
    def use_move(self, move_name, opponent_pokemon, type_effectiveness):
        """
        Use the input move to attack the opponent pokemon.

        Parameters:
        - move_name: string with the name of the move to be used.
        - opponent_pokemon: PokemonCharacter object representing the pokemon that is being attacked.
        - type_effectiveness: dictionary with type effectivenesses of moves.
                              type_effectiveness["attack_type"]["defend_type"] is a float with the type effectiveness of a move of type "attack_type" against a pokemon of type "defend_type".
        """

        # get the selected move from the moves of the pokemon
        move = None
        for m in self.moves:
            if m["name"] == move_name:
                move = m
                break

        # # print some information about the move
        # type_text(f"{self.name} uses {move_name}!\n")

        # # reduce the power points (pp) of the move, independently of whether the move succeeds or not
        # self.curr_pps[move_name] -= 1

        # the move succeeds with a probability equal to its accuracy
        if random.random() < move["accuracy"]:

            # compute the effect modifier based on the move type and on the opponent pokemon type
            effect = 1
            for opponent_type in opponent_pokemon.types:
                effect *= type_effectiveness[move["type"]][opponent_type]

            # compute the damage dealt by the move to the opponent pokemon
            stability = 1.5 if move["type"] in self.types else 1.0
            critical = 2 if random.random() < (self.base_stats["speed"] / 512) else 1
            luck = random.uniform(0.85, 1.0)
            modifier = stability * effect * critical * luck
            attack = self.base_stats["attack"] if move["category"] == "physical" else self.base_stats["special"]
            defense = opponent_pokemon.base_stats["defense"] if move["category"] == "physical" else opponent_pokemon.base_stats["special"]
            damage = math.floor(((2 * self.level + 10) / 250 * (attack / defense) * move["power"] + 2) * modifier)

            # apply the damage to the opponent pokemon
            opponent_pokemon.curr_hp -= damage

            # # print some information about the move
            # type_text(f"It dealt a damage of {damage} HP to {opponent_pokemon.name}.\n")
        
        # # if the move fails, just print information
        # else:
        #     type_text(f"{self.name}'s {move_name} missed!\n")
