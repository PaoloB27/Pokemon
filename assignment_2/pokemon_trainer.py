class PokemonTrainer:
    """
    Class defining the main character of the Pokemon game, that is, the Pokemon Trainer, controlled by the player.
    """

    # maximum number of pokemon that a pokemon trainer can have
    max_n_pokemon = 6

    def __init__(self, name, pokemon_list=None):
        """
        A PokemonTrainer is the main character of the Pokemon game, controlled by the player.
        In addition to the below parameters, the pokemon trainer is initialized with an empty dictionary of items that the trainer can use.

        Parameters:
        - name: string with the name of the pokemon trainer.
        - pokemon_list: list with the pokemon that the pokemon trainer has.
                        The maximum number of pokemon that a pokemon trainer can have is max_n_pokemon.
                        If the list has more than max_n_pokemon pokemon, an error is raised.
        """

        # name of the pokemon trainer
        self.name = name

        # list with the pokemon that the pokemon trainer has
        if pokemon_list is None:
            self.pokemon_list = []
        elif len(pokemon_list) > PokemonTrainer.max_n_pokemon:
            raise ValueError(f"A pokemon trainer can have at most {PokemonTrainer.max_n_pokemon} pokemon.")
        else:
            self.pokemon_list = pokemon_list

        # initialize the dictionary of items that can be used by the pokemon trainer as empty
        self.items = {}
    
    def add_item(self, item, quantity=1):
        """
        Adds an item to the pokemon trainer's dictionary of items.

        Parameters:
        - item: string with the name of the item to be added.
        - quantity: integer with the number of items to be added. Default is 1.
                    If the item is already present in the dictionary, then its quantity is increased by the input quantity.
        """

        # increase the quantity of the item
        if item in self.items:
            self.items[item] += quantity
        
        # add the item with the input quantity
        else:
            self.items[item] = quantity
        print(f"{quantity} {item}s added to your items. Now you have {self.items[item]} {item}s.")