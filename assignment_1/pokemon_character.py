class PokemonCharacter:
    """
    Class to represent a pokemon in the pokemon game.
    """

    def __init__(self, name, types=["normal"]):
        """
        A pokemon character is initialized by setting the parameters below.

        Parameters:
        - name: string with the name of the pokemon.
        - types: list with the types of the pokemon. By default, the pokemon is of type "normal".
        - base_stats: dictionary with the base stats of the pokemon.
                      The dictionary must include:
                      - "hp": integer with the maximum health points of the pokemon.
                      - "attack": integer with the attack power of the pokemon.
                      - "defense": integer with the defense power of the pokemon.
                      - "speed": integer with the speed of the pokemon.
                      - "special": integer used to attack and defend with special moves.
        - moves: list of dictionaries containing the moves that the pokemon can make during a battle.
                 Each move is a dictionary that must include:
                 - "name": string with the name of the move.
                 - "type": string with the type of the move.
                 - "category": string with the category of the move. It can be "physical" or "special".
                 - "power": integer with the power of the move.
                 - "accuracy": float representing the probability of hitting the opponent pokemon with the move.
                 - "pp": integer with the maximum number of times that the move can be used.
        """

        # name of the pokemon
        self.name = name

        # initialize the level of the pokemon to 1
        self.level = 1

        # set the types of the pokemon
        self.types = types

