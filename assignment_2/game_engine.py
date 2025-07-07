import random
from pokemon_trainer import PokemonTrainer
from pokemon_character import PokemonCharacter
from pokemon_moves import moves
from pokemon import starter_pokemon, wild_pokemon
from utils import clear_terminal, type_text, choose_option

def pokemon_from_dict(pokemon_info):
    """
    Initializes a PokemonCharacter object from an input dictionary.

    Parameters:
    - pokemon_info: dictionary that must have the following entries:
                    - name: string with the name of the pokemon;
                    - base_stast: dictionary with the basic statistics of the pokemon;
                    - moves: list of strings with the names of the moves of the pokemon;
                    - national_pokedex_number: integer resperenting the national pokedex number of the pokemon;
                    - types: list of strings with the types of the pokemon.
    
    Returns:
    - pokemon: PokemonCharacter initialized with the input information.
    """

    # initialize a PokemonCharacter with the input information
    moves_dict = {move["name"]: move for move in moves}
    pokemon = PokemonCharacter(
        name=pokemon_info["name"],
        national_pokedex_number=pokemon_info["national_pokedex_number"],
        types=pokemon_info["types"],
        base_stats=pokemon_info["base_stats"],
        moves=[moves_dict[m] for m in pokemon_info["moves"]]
    )

    return pokemon

def initialize_pokemon_trainer():
    """
    Initializes a PokemonTrainer with:
    - a name chosen by the user;
    - a starter pokemon chosen by the user among Charmander, Squirtle and Bulbasaur;
    - 10 potions and 10 pokeballs as items.

    Returns:
    - trainer: PokemonTrainer object representing the initialized pokemon trainer.
    """

    # ask the user (i.e., the pokemon trainer) to enter his name
    type_text("\nHello pokemon trainer! What is your name?\n")
    trainer_name = input("> ")
    clear_terminal()
    
    # create the pokemon trainer
    trainer = PokemonTrainer(trainer_name)

    # make the user choose the starter pokemon
    starter_pokemon_choice = choose_option([pokemon["name"] for pokemon in starter_pokemon], f"Ok {trainer_name}, I want you to choose one of the following pokemon:")
    clear_terminal()

    # create the starter pokemon and add it to the pokemon trainer's list
    chosen_pokemon = starter_pokemon[int(starter_pokemon_choice)]
    chosen_pokemon = pokemon_from_dict(chosen_pokemon)
    type_text(f"You chose {chosen_pokemon.name}! Great choice {trainer_name}!\n\n")
    trainer.add_pokemon(chosen_pokemon)

    # add 10 potions and 10 pokeballs to the pokemon trainer's items
    trainer.add_items("potion", 10)
    trainer.add_items("pokeball", 10)

    return trainer

def attack(pokemon_trainer, opponent_pokemon):
    """
    The active pokemon of the pokemon trainer attacks the opponent pokemon.

    Parameters:
    - pokemon_trainer: PokemonTrainer object representing the character that leads the battle.
    - opponent_pokemon: PokemonCharacter object representing the pokemon that receives the attack.

    Returns:
    - is_defeated: boolean indicating whether the opponent pokemon is defeated or not.
    """

    # make the pokemon trainer choose a move
    possible_moves = [move['name'] for move in pokemon_trainer.active_pokemon.moves]
    options = [f"{move_name} | {pp} PP" for move_name, pp in pokemon_trainer.active_pokemon.curr_pps.items()]
    chosen_move = possible_moves[choose_option(options, question_sentence=f"Which move do you want {pokemon_trainer.active_pokemon.name} to use?")]

    # make the active pokemon attack the opponent pokemon with the chosen move
    pokemon_trainer.active_pokemon.use_move(chosen_move, opponent_pokemon)

    # check whether the opponent pokemon is defeated and end the battle in this case
    if opponent_pokemon.curr_hp <= 0:
        type_text(f"\nCongratulations! The wild {opponent_pokemon.name} is defeated!\n")
        return True
    
    # the opponent pokemon is not difeated
    return False

def use_item(pokemon_trainer, opponent_pokemon):
    """
    Makes the pokemon trainer choose an item among the available ones and applies it.

    Parameters:
    - pokemon_trainer: PokemonTrainer object representing the character that leads the battle.
    - opponent_pokemon: PokemonCharacter object representing the opponent pokemon in the battle.

    Returns:
    - is_catched: boolean indicating whether the opponent pokemon is catched or not, in case the item to use is a pokeball.
                  If the item to use is not a pokeball, then it returns False.
    """

    # make the trainer choose which item has to be used
    items = [item_name for item_name in pokemon_trainer.items.keys()]
    options = [f"{item_name} | {quantity}" for item_name, quantity in pokemon_trainer.items.items()]
    chosen_item = items[choose_option(options, "What item do you want to use?")]

    # apply a potion to the pokemon trainer's active pokemon
    if chosen_item == "potion":
        pokemon_trainer.use_potion()
        return False
    
    # use a pokeball to try to catch the opponent pokemon
    elif chosen_item == "pokeball":
        
        # there is space for a new pokemon in the trainer's list
        try:
            
            # the pokemon has been catched
            if pokemon_trainer.use_pokeball(opponent_pokemon):
                return True
            
            # the pokemon has not been catched
            return False
        
        # there is not space for a new pokemon in the trainer's list, but the pokemon has been catched and freed, so the battle ends
        except OverflowError:
            type_text(f"The catched {opponent_pokemon.name} is left free and the used pokeball is thrown away.\n")
            return True

def run_away(pokemon_trainer, opponent_pokemon):
    """
    Makes the pokemon trainer try to run away from the encountered wild pokemon.

    Parameters:
    - pokemon_trainer: PokemonTrainer object representing the character that leads the battle.
    - opponent_pokemon: PokemonCharacter object representing the opponent pokemon in the battle.

    Returns:
    - is_escaped: boolean indicating whether the pokemon trainer has run away or not.
    """

    # print some information
    type_text(f"{pokemon_trainer.name} wants to run away.\n")

    # probability of running away
    run_prob = 0.6

    # the pokemon trainer successfully runs away, so the battle is over
    if random.random() < run_prob:
        type_text(f"{pokemon_trainer.name} ran away, the battle is over.\n")
        return True
    
    # the pokemon trainer fails to run away, so the battle goes on
    type_text(f"{opponent_pokemon.name} prevents {pokemon_trainer.name} to run away, the battle continues!\n")
    return False

def change_pokemon(pokemon_trainer):
    """
    Changes the active pokemon during a battle.

    Parameters:
    - pokemon_trainer: PokemonTrainer object representing the character that leads the battle.

    Returns:
    - True if the change has been successful, False if the change cannot be made.
    """

    # pokemon that can be selected for the change
    available_pokemon = [pokemon.name for pokemon in pokemon_trainer.pokemon_list if pokemon is not pokemon_trainer.active_pokemon and pokemon.curr_hp > 0]
    available_pokemon_to_display = [f"{pokemon.name} | {pokemon.curr_hp} HP" for pokemon in pokemon_trainer.pokemon_list if pokemon is not pokemon_trainer.active_pokemon and pokemon.curr_hp > 0]
    
    # there is at least a pokemon that can be used
    if available_pokemon:
        chosen_pokemon = available_pokemon[choose_option(available_pokemon_to_display, "What pokemon do you want to become active?")]
        pokemon_trainer.change_active_pokemon(chosen_pokemon)
        return True
    
    # there is no pokemon that can be used
    type_text(f"You cannot change {pokemon_trainer.active_pokemon.name}!\n")
    return False

def opponent_pokemon_turn(pokemon_trainer, opponent_pokemon):
    """
    Makes the opponent pokemon attack the active pokemon of the trainer.
    If the trainer's active pokemon is defeated, then a new active pokemon is chosen in the trainer's list, if any.
    If there is no pokemon in the trainer's list that is not K.O., then True is returned.

    Parameters:
    - pokemon_trainer: PokemonTrainer object representing the character that leads the battle.
    - opponent_pokemon: PokemonCharacter object representing the opponent pokemon in the battle.

    Returns:
    - is_defeated: boolean indicating whether all pokemon of the pokemon trainer have been defeated or not.
    """

    # make the opponent pokemon attack the trainer's active pokemon with a move sampled uniformly at random among the available ones
    type_text(f"\nIt's the turn of {opponent_pokemon.name} now!\n\n")
    opponent_pokemon.use_move(random.choice([move["name"] for move in opponent_pokemon.moves]), pokemon_trainer.active_pokemon)
    
    # check whether the trainer's active pokemon is defeated
    if pokemon_trainer.active_pokemon.curr_hp <= 0:
        
        # print some information
        type_text(f"\n{pokemon_trainer.active_pokemon.name} is defeated!\n")

        # if all trainer's pokemon are defeated, then the battle ends and the pokemon trainer has to go to the pokemon center
        if not change_pokemon(pokemon_trainer):
            type_text(f"\nAll {pokemon_trainer.name}'s pokemon are K.O., so {pokemon_trainer.name} loses the battle!\n")
            return True
    
    # the battle is not ended
    return False

def battle(pokemon_trainer, opponent_pokemon):
    """
    Runs a battle against an opponent pokemon.

    Parameter:
    - pokemon_trainer: PokemonTrainer object representing the character that leads the battle.
    """

    # options among which the pokemon trainer has to choose during an iteration of the battle
    options = ["Attack", "Change Pokemon", "Use Item", "Run Away"]

    # print some information
    type_text(f"\nThe battle against {opponent_pokemon.name} begins!\n")

    # the battle goes on until the opponent is catched or the opponent is defeated or the trainer runs away or all the trainer's pokemon are defeated.
    round = 1
    while True:

        # print the round number and the health points of the two pokemon involved in the battle
        type_text(f"\nRound {round}\n")
        type_text(f"\n{pokemon_trainer.active_pokemon.name} HP: {pokemon_trainer.active_pokemon.curr_hp}\n")
        type_text(f"{opponent_pokemon.name} HP: {opponent_pokemon.curr_hp}\n")

        # make the pokemon trainer choose what to do in this iteration
        type_text(f"\nIt's the turn of {pokemon_trainer.active_pokemon.name}.\n")
        choice_id = choose_option(options)

        # the pokemon trainer decides to attack
        if choice_id == 0:
            if attack(pokemon_trainer, opponent_pokemon):
                return                                      # the battle ends, because the opponent pokemon is defeated

        # the pokemon trainer wants to change the active pokemon
        elif choice_id == 1:
            if not change_pokemon(pokemon_trainer):
                continue                                    # the change cannot be done, because the active pokemon is the only pokemon left, so the user must choose another option
        
        # the pokemon trainer wants to use an item
        elif choice_id == 2:

            # there are no items in the trainer's dictionary
            if not pokemon_trainer.items:
                type_text("\nYou do not have any item in your backpack. Choose another option.\n")
                continue                                  # the user needs to select another action, because it is not possible to use items

            # make the user choose an item and use it
            if use_item(pokemon_trainer, opponent_pokemon):
                return                                    # the battle ends, because the opponent pokemon has been catched
        
        # the pokemon trainer wants to run away
        elif choice_id == 3:
            if run_away(pokemon_trainer, opponent_pokemon):
                return                                    # the battle ends, becasue the pokemon trainer has run away

        # make the opponent pokemon attack the trainer's active pokemon with a move sampled uniformly at random among the available ones
        if opponent_pokemon_turn(pokemon_trainer, opponent_pokemon):
            
            # the pokemon trainer goes to the pokemon center since all trainer's pokemon are K.O.
            pokemon_center_action(pokemon_trainer)
            
            return                                        # the battle ends, because the trainer's pokemon are K.O.

        # update the round number
        round += 1

def explore_action(pokemon_trainer):
    """
    Makes the pokemon trainer explore the world, with a given probability of finding a wild pokemon opponent.

    Parameter:
    - pokemon_trainer: PokemonTrainer object representing the character that takes the action.
    """

    # probability of finding a wild pokemon
    p = 0.8

    # print some information
    clear_terminal()
    type_text("Exploring the Pokemon World")
    type_text(" ...", delay=0.5)
    type_text("\n\n")

    # a wild pokemon has been encountered
    if random.random() <= 0.8:
        
        # sample uniformly at random a wild pokemon among the loaded ones
        sampled_pokemon = pokemon_from_dict(random.choice(wild_pokemon))

        # print some information
        type_text(f"A wild {sampled_pokemon.name} appears!\n")

        # start a battle against the sampled wild pokemon
        battle(pokemon_trainer, sampled_pokemon)
    
    # no wild pokemon has been encounterd
    else:
        type_text("There is no wild pokemon around.\n")

def pokemon_center_action(pokemon_trainer):
    """
    Makes the pokemon trainer go to the pokemon center, restoring the HP of every pokemon in the trainer's list and the PP of all the moves of all pokemon.

    Parameter:
    - pokemon_trainer: PokemonTrainer object representing the character that takes the action.
    """
    
    # print some information
    clear_terminal()
    type_text("Welcome to the Pokemon Center!\n\nWe are restoring the HP and PP of all your pokemon")
    type_text(" ...", delay=0.5)
    type_text("\n")

    # restore the hp of every pokemon in the pokemon trainer's list
    for pokemon in pokemon_trainer.pokemon_list:
        pokemon.curr_hp = pokemon.base_stats["hp"]
    
    # restore the pp of every move of each pokemon
    for pokemon in pokemon_trainer.pokemon_list:
        for move in pokemon.moves:
            move_name = move["name"]
            pokemon.curr_pps[move_name] = move["pp"]

    # print some information
    type_text("\nAll your pokemon are restored.\n\nHope not to see you soon!\n")

def pokemon_store_action(pokemon_trainer):
    """
    Makes the pokemon trainer go to the pokemon store to fill all the trainer's items to their maximum: 10 potions and 10 pokeballs.

    Parameter:
    - pokemon_trainer: PokemonTrainer object representing the character that takes the action.
    """

    # items present in the store
    store_items = ["potion", "pokeball"]

    # print some information
    clear_terminal()
    type_text("Hello, happy to see you at the Pokemon Store.\n\nHere we go with the items you ordered")
    type_text(" ...", delay=0.5)
    type_text("\n\n")

    # check the current quantities for the items present in the store that the trainer has
    curr_items_quantities = {}
    for item in store_items:
        curr_items_quantities[item] = pokemon_trainer.items.get(item, 0)    # set the value to 0 if the item is not in pokemon_trainer.items

    # fill the pokemon trainer's items
    for item in store_items:
        quantity_to_sell = 10 - curr_items_quantities[item]
        pokemon_trainer.add_items(item, quantity_to_sell)

    # print some information
    type_text("\nThank you for purchasing! See you soon!\n")

def run_game():
    """
    Runs the game.
    """

    # initialize the pokemon trainer
    trainer = initialize_pokemon_trainer()

    # print a welcome message
    type_text(f"\nWelcome to the Pokemon World, {trainer.name}!\n")

    # actions among which the player can choose
    actions = ["Explore", "Go to the Pokemon Center", "Go to the Pokemon Store", "Quit"]

    # make the player play until the player decides to quit
    while True:

        # make the player choose the next action
        chosen_id = choose_option(actions)

        # run the action selected by the user
        if chosen_id == 0:
            explore_action(trainer)
        elif chosen_id == 1:
            pokemon_center_action(trainer)
        elif chosen_id == 2:
            pokemon_store_action(trainer)
        elif chosen_id == 3:
            type_text("\nThe game has been successfully closed. Thank you for playing!\n")
            break
