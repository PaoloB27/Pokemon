class PokemonTrainer:
    """
    Class defining the main character of the Pokemon game, that is, the Pokemon Trainer, controlled by the player.
    """

    # maximum number of pokemon that a pokemon trainer can have
    max_n_pokemon = 6

    def __init__(self, name, pokemon_list=None):
        """
        A PokemonTrainer is the main character of the Pokemon game, controlled by the player.
        In addition to the below parameters, the pokemon trainer is initialized with an empty list of items that the trainer can use.

        Parameters:
        - name: string with the name of the pokemon trainer.
        - pokemon_list: list with the pokemon that the pokemon trainer has.
                        The maximum number of pokemon that a pokemon trainer can have is MAX_N_POKEMON.
                        If the list has more than MAX_N_POKEMON pokemon, an error is raised.
        """

        # name of the pokemon trainer
        self.name = name

        # list with the pokemon that the pokemon trainer has
        if pokemon_list is None:
            self.pokemon_list = []
        elif len(pokemon_list) > PokemonTrainer.MAX_N_POKEMON:
            raise ValueError("A pokemon trainer can have at most 6 pokemon.")
        else:
            self.pokemon_list = pokemon_list

        # initialize the list of items that can be used by the pokemon trainer as empty
        self.items = []
    