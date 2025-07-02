from pokemon_trainer import PokemonTrainer
from pokemon_character import PokemonCharacter
from pokemon_and_moves import starter_pokemon

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
    trainer_name = input("Hello pokemon trainer! What is your name?\n")
    
    # create the pokemon trainer
    trainer = PokemonTrainer(trainer_name)

    # make the user choose the starter pokemon
    print(f"Ok {trainer_name}, I want you to choose one of the following pokemon:")
    for i, pokemon in enumerate(starter_pokemon):
        print(f"{i}: {pokemon["name"]}")
    starter_pokemon_choice = input("Tell me the number of the pokemon you want: ")

    # create the starter pokemon and add it to the pokemon trainer's list
    chosen_pokemon = starter_pokemon[int(starter_pokemon_choice)]
    moves = {move["name"]: move for move in moves}
    chosen_pokemon = PokemonCharacter(
        name=chosen_pokemon["name"],
        national_pokedex_number=chosen_pokemon["national_pokedex_number"],
        types=chosen_pokemon["types"],
        base_stats=chosen_pokemon["base_stats"],
        moves=[moves[m] for m in chosen_pokemon["moves"]]
    )
    print(f"You chose {chosen_pokemon.name}! Great choice {trainer_name}!")
    trainer.pokemon_list.append(chosen_pokemon)

    # add 10 potions and 10 pokeballs to the pokemon trainer's items
    trainer.add_item("potion", 10)
    trainer.add_item("pokeball", 10)

    return trainer

def explore_action(pokemon_trainer):
    """
    """
    pass

def pokemon_center_action(pokemon_trainer):
    """
    """
    pass

def pokemon_store_action(pokemon_trainer):
    """
    """
    pass

def run_action(pokemon_trainer, action):
    """
    Runs the action provided as input.

    Parameters:
    - pokemon_trainer: PokemonTrainer object that is acting in the Pokemon World.
    - action: string that indicates which action must be run. It must be "explore", "pokemon center" or "pokemon store".
    """

    # run the appropriate action
    if action == "explore":
        explore_action(pokemon_trainer)
    elif action == "pokemon center":
        pokemon_center_action(pokemon_trainer)
    elif action == "pokemon store":
        pokemon_store_action(pokemon_trainer)

def run_game(trainer):
    """
    Runs the game.

    Parameters:
    - trainer: PokemonTrainer object representing the pokemon trainer.
    """

    # print a welcome message
    print(f"Welcome to the Pokemon World, {trainer.name}!")

    # actions among which the player can choose
    actions = ["explore", "pokemon center", "pokemon store", "quit"]

    # make the player play until the player decides to quit
    while True:

        # make the player choose the next action
        print("Choose one of the following actions:")
        for i, action in enumerate(actions):
            print(f"{i}: {action}")
        input("Enter the number of the action you select: ")
