import random
from pokemon_trainer import PokemonTrainer
from pokemon_character import PokemonCharacter
from pokemon_and_moves import starter_pokemon, moves

def choose_option(options, question_sentence="What do you want to do?"):
    """
    Makes the user choose among one of the items in the input list and returns the choice.

    Parameters:
    - options: list of strings with the names of the options to choose among to be displayed to the user.
    - question

    Returns:
    - choice_id: integer representing the index of the chosen option in the list options.
    """
    
    # iterate while the user types a valid option
    while True:

        # make the use choose an option
        print(f"\n{question_sentence}")
        for i, option in enumerate(options):
            print(f"{i}: {option}")
        
        # check whether the option is valid
        no_int = False
        try:
            choice_id = int(input("Enter the number of your choice: "))
        except ValueError:
            no_int = True
        if no_int or choice_id < 0 or choice_id >= len(options):
            print("Invalid choice. Please, choose one of the numbers displayed for the options.")
            continue

        # the option is valid
        return choice_id

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
    trainer_name = input("\nHello pokemon trainer! What is your name?\n")
    
    # create the pokemon trainer
    trainer = PokemonTrainer(trainer_name)

    # make the user choose the starter pokemon
    print(f"Ok {trainer_name}, I want you to choose one of the following pokemon:")
    for i, pokemon in enumerate(starter_pokemon):
        print(f"{i}: {pokemon["name"]}")
    starter_pokemon_choice = input("Tell me the number of the pokemon you want: ")

    # create the starter pokemon and add it to the pokemon trainer's list
    chosen_pokemon = starter_pokemon[int(starter_pokemon_choice)]
    moves_dict = {move["name"]: move for move in moves}
    chosen_pokemon = PokemonCharacter(
        name=chosen_pokemon["name"],
        national_pokedex_number=chosen_pokemon["national_pokedex_number"],
        types=chosen_pokemon["types"],
        base_stats=chosen_pokemon["base_stats"],
        moves=[moves_dict[m] for m in chosen_pokemon["moves"]]
    )
    print(f"You chose {chosen_pokemon.name}! Great choice {trainer_name}!")
    trainer.pokemon_list.append(chosen_pokemon)

    # add 10 potions and 10 pokeballs to the pokemon trainer's items
    trainer.add_item("potion", 10)
    trainer.add_item("pokeball", 10)

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
    possible_moves = pokemon_trainer.active_pokemon.moves
    chosen_move = possible_moves[choose_option(possible_moves, question_sentence=f"Which move do you want {pokemon_trainer.active_pokemon.name} to do?")]

    # make the active pokemon attack the opponent pokemon with the chosen move
    pokemon_trainer.active_pokemon.use_move(chosen_move, opponent_pokemon)

    # check whether the opponent pokemon is defeated and end the battle in this case
    if opponent_pokemon.curr_hp <= 0:
        print(f"\nCongratulations! The wild {opponent_pokemon.name} is defeated!")
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
    options = [item_name for item_name in pokemon_trainer.items.keys()]
    chosen_item = options[choose_option(options, "What item do you want to use?")]

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
            print(f"The catched {opponent_pokemon.name} is left free and the used pokeball is thrown away.")
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
    print(f"{pokemon_trainer.name} wants to run away.")

    # probability of running away
    run_prob = 0.6

    # the pokemon trainer successfully runs away, so the battle is over
    if random.random < run_prob:
        print(f"{pokemon_trainer.name} ran away, the battle is over.")
        return True
    
    # the pokemon trainer fails to run away, so the battle goes on
    print(f"{opponent_pokemon.name} prevents {pokemon_trainer.name} to run away, the battle continues!")
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
    print(f"\nIt's the turn of {opponent_pokemon.name} now!")
    opponent_pokemon.use_move(random.choice([move.name for move in opponent_pokemon.moves]), pokemon_trainer.active_pokemon)
    
    # check whether the trainer's active pokemon is defeated
    if pokemon_trainer.active_pokemon.curr_hp <= 0:
        
        # print some information
        print(f"{pokemon_trainer.active_pokemon.name} is defeated!")

        # change the defeated active pokemon with another pokemon in the trainer's list that is not K.O., if any
        not_ko_pokemons = [pokemon for pokemon in pokemon_trainer.pokemon_list if pokemon.curr_hp > 0]
        if not_ko_pokemons:
            print(f"{pokemon_trainer.name} chooses {not_ko_pokemons[0].name} to join the battle!")
            pokemon_trainer.active_pokemon = not_ko_pokemons[0]
        
        # if all trainer's pokemon are defeated, then the battle ends and the pokemon trainer has to go to the pokemon center
        else:
            print(f"All {pokemon_trainer.name}'s pokemon are K.O., so {pokemon_trainer.name} loses the battle!")
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
    print(f"\nThe battle against {opponent_pokemon.name} has begun!")

    # the battle goes on until the opponent is catched or the opponent is defeated or the trainer runs away or all the trainer's pokemon are defeated.
    round = 1
    while True:

        # print the round number and the health points of the two pokemon involved in the battle
        print(f"\nRound {round}")
        print(f"\n{pokemon_trainer.active_pokemon.name} HP: {pokemon_trainer.active_pokemon.curr_hp}")
        print(f"{opponent_pokemon.name} HP: {opponent_pokemon.curr_hp}")

        # make the pokemon trainer choose what to do in this iteration
        print(f"\nIt's the turn of {pokemon_trainer.active_pokemon}")
        choice_id = choose_option(options)

        # the pokemon trainer decides to attack
        if choice_id == 0:
            if attack(pokemon_trainer, opponent_pokemon):
                return                                      # the battle ends, because the opponent pokemon is defeated

        # the pokemon trainer wants to change the active pokemon
        elif choice_id == 1:
            options = [pokemon.name for pokemon in pokemon_trainer.pokemon_list]
            chosen_pokemon = options[choose_option(options, "What pokemon do you want to become active?")]
            pokemon_trainer.change_active_pokemon(chosen_pokemon)
        
        # the pokemon trainer wants to use an item
        elif choice_id == 2:

            # there are no items in the trainer's dictionary
            if not pokemon_trainer.items:
                print("\nYou do not have any item in your backpack. Choose another option")
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
    print("\nExploring the Pokemon World...")

    # a wild pokemon is found with probability p and a battle is started, otherwise nothing happens
    if random.random() <= 0.8:
        battle(pokemon_trainer)
    else:
        print("There is no wild pokemon around.")

def pokemon_center_action(pokemon_trainer):
    """
    Makes the pokemon trainer go to the pokemon center, restoring the HP of every pokemon in the trainer's list and the PP of all the moves of all pokemon.

    Parameter:
    - pokemon_trainer: PokemonTrainer object representing the character that takes the action.
    """
    
    # print some information
    print("\nWelcome to the Pokemon Center!\nWe are restoring the HP and PP of all your pokemon...")

    # restore the hp of every pokemon in the pokemon trainer's list
    for pokemon in pokemon_trainer:
        pokemon.curr_hp = pokemon.base_stats["hp"]
    
    # restore the pp of every move of each pokemon
    for pokemon in pokemon_trainer:
        for move in pokemon.moves:
            move_name = move["name"]
            pokemon.curr_pps[move_name] = move["pp"]

    # print some information
    print("All your pokemon are restored.\nHope not to see you soon!")

def pokemon_store_action(pokemon_trainer):
    """
    Makes the pokemon trainer go to the pokemon store to fill all the trainer's items to their maximum: 10 potions and 10 pokeballs.

    Parameter:
    - pokemon_trainer: PokemonTrainer object representing the character that takes the action.
    """

    # items present in the store
    store_items = ["potions", "pokeballs"]

    # print some information
    print("\nHello, happy to see you at the Pokemon Store.\nHere we go with the items you ordered...")

    # check the current quantities for the items present in the store that the trainer has
    curr_items_quantities = {}
    for item in store_items:
        curr_items_quantities[item] = pokemon_trainer.items.get(item, 0)    # set the value to 0 if the item is not in pokemon_trainer.items

    # fill the pokemon trainer's items
    for item in store_items:
        quantity_to_sell = 10 - curr_items_quantities[item]
        pokemon_trainer.add_items(item, quantity_to_sell)
        print(f"Added {quantity_to_sell} {item}s: now you have {pokemon_trainer.items[item]} {item}s.")

    # print some information
    print("Thank you for purchasing! See you soon!")

def run_game():
    """
    Runs the game.

    Parameters:
    - trainer: PokemonTrainer object representing the pokemon trainer.
    """

    # initialize the pokemon trainer
    trainer = initialize_pokemon_trainer()

    # print a welcome message
    print(f"Welcome to the Pokemon World, {trainer.name}!")

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
            print("\nThe game has been successfully closed. Thank you for playing!")
            break
