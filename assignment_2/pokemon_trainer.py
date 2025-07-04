import random

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
        The active pokemon will be initialized as the first pokemon in pokemon_list if it is not None nor empty, to None otherwise.

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
            raise OverflowError(f"A pokemon trainer can have at most {PokemonTrainer.max_n_pokemon} pokemon.")
        else:
            self.pokemon_list = pokemon_list

        # initialize the active pokemon to the first pokemon in the list if the list is not empty, to None otherwise
        self.active_pokemon = None if self.pokemon_list == [] else self.pokemon_list[0]

        # initialize the dictionary of items that can be used by the pokemon trainer as empty
        self.items = {}
    
    def add_items(self, item, quantity=1):
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
        print(f"\n{quantity} {item}s added to your items. Now you have {self.items[item]} {item}s.")
    
    def decrease_item(self, item):
        """
        Decreases by 1 the quantity of the item with the input name in the trainer's dictionary of items.
        If there are no more items, the (key, value) pair with item as key is removed from self.items.

        Parameters:
        - item: item to be decreased by 1.
        """

        # no need to decrease the item's quantity, since it is not present in the trainer's dictionary of items.
        if item not in self.items:
            return
        
        # decrease the quantity of the input item by 1
        self.items[item] -= 1

        # remove the item from the dictionary since its quantity is 0
        if self.items[item] == 0:
            del self.items[item]

    def use_potion(self):
        """
        Uses a potion on the active pokemon, if present in the dictionary of items of the trainer.
        Otherwise, a ValueError exception is raised.
        """

        # give a potion to the active pokemon, if there is a potion among the trainer's items
        if "potion" in self.items:
            self.active_pokemon.curr_hp += 20
            if self.active_pokemon.curr_hp > self.active_pokemon.base_stast["hp"]:
                self.active_pokemon.curr_hp = self.active_pokemon.base_stast["hp"]
                self.decrease_item("potion")

        # there are not potions in the dictionary of items
        raise ValueError("there are not potions in your backpack.")
    
    def use_pokeball(self, opponent_pokemon):
        """
        Tries to catch the input opponent pokemon if there are pokeballs in the trainer's dictionary of items.
        Otherwise, a ValueError exception is raised.
        It raises an OverfullError exception if the list of pokemon is full and the captured pokemon cannot be added.

        Parameters:
        - opponent_pokemon: opponent pokemon that the trainer wants to catch.

        Returns:
        - captured: boolean indicating whether the opponent pokemon has been successfully catched.
        """

        # there are pokeballs in the trainer's dictionary of items
        if "pokeball" in self.items:

            # decrease the available pokeballs
            self.decrease_item("pokeball")
            print(f"{self.name} uses a Pokeball!")

            # probability of catching the opponent pokemon
            catch_probability = 1 - opponent_pokemon.curr_hp / opponent_pokemon.base_stats["hp"]

            # the pokemon is catched
            if random.random < catch_probability:
                print(f"1... 2... 3... Yes! Congratulations {self.name}, you catched a {opponent_pokemon.name}!")
                
                # there is no more space for a new pokemon
                if len(self.pokemon_list) >= self.max_n_pokemon:
                    print(f"Oh, no! You do not have enough space for your new {opponent_pokemon.name}!")
                    raise OverflowError("Your list of pokemon is full.")
                
                # add the pokemon to the trainer's list
                else:
                    self.pokemon_list.append(opponent_pokemon)
                    return True

            # the pokemon broke free        
            else:
                print(f"1... 2... 3... Oh, no! the wild {opponent_pokemon.name} broke free!")
                return False

        # there are not pokeballs in the dictionary of items
        else:
            raise ValueError("there are not pokeballs in your backpack.")

    def add_pokemon(self, new_pokemon):
        """
        Adds a new pokemon to the trainer's list of pokemon.
        If there are already max_n_pokemon in the list, the function raises a OverflowError exception.

        Parameters:
        - new_pokemon: pokemon to be added to the trainer's list.
        """

        # raise an OverflowError exception if the list is already full
        if len(self.pokemon_list) >= self.max_n_pokemon:
            raise OverflowError(f"Your list of pokemon is full!\nA pokemon trainer can have at most {PokemonTrainer.max_n_pokemon} pokemon.")
        
        # otherwise, add the pokemon to the trainer's list
        self.pokemon_list.append(new_pokemon)

        # if the added pokemon is the only one in the list, then set it as the active pokemon
        if len(self.pokemon_list) == 1:
            self.active_pokemon = self.pokemon_list[0]
    
    def change_active_pokemon(self, new_active_pokemon_name):
        """
        Changes the active pokemon by setting as new active pokemon the one in the trainer's list with name new_active_pokemon_name.

        Parameters:
        - new_active_pokemon_name: name of the pokemon in the trainer's list to set as active pokemon.
        """

        # find the pokemon in the trainer's list with the input name and set it as the active pokemon
        for pokemon in self.pokemon_list:
            if pokemon.name == new_active_pokemon_name:
                self.active_pokemon = pokemon
                return
        
        # there is no pokemon in the trainer's list with the input name, so raise a ValueError
        raise ValueError(f"{new_active_pokemon_name} is not in your list of Pokemon")