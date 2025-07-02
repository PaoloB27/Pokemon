import random
from pokemon_trainer import PokemonTrainer
from pokemon_character import PokemonCharacter
from pokemons_and_moves import starter_pokemon, moves

# main function that runs the script
if __name__ == '__main__':

    # ask to the user (i.e., the pokemon trainer) his name
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

    # choose an enemy pokemon uniformly at random among those not selected by the pokemon trainer
    enemy_pokemon = random.choice([p for p in starter_pokemon if p["name"] != trainer.pokemon_list[0].name])
    enemy_pokemon = PokemonCharacter(
        name=enemy_pokemon["name"],
        national_pokedex_number=enemy_pokemon["national_pokedex_number"],
        types=enemy_pokemon["types"],
        base_stats=enemy_pokemon["base_stats"],
        moves=[moves[m] for m in enemy_pokemon["moves"]]
    )

    # make the battle going on until the pokemon trainer decides to stop or the pokemon faints
    print(f"\nLet's test some of the moves of your {trainer.pokemon_list[0].name} against my {enemy_pokemon.name}.")
    print(f"{enemy_pokemon.name} HP: {enemy_pokemon.base_stats['hp']}")
    round = 1
    while True:

        # print information on the round
        print(f"\nRound {round}!")

        # ask the pokemon trainer to choose a move
        print("The moves available for your pokemon are:")
        for i, move in enumerate(trainer.pokemon_list[0].moves):
            print(f"{i}: {move['name']} (PP: {move['pp']})")
        move = input("Choose a move by typing its number or press q to end the battle: ")
        if move == 'q':
            print("Battle ended. Thanks for playing!")
            break
        move = int(move)
        if move < 0 or move >= len(trainer.pokemon_list[0].moves):
            print("Invalid choice! Please choose a valid move number.")
            continue
        move_name = trainer.pokemon_list[0].moves[move]["name"]

        # check that the move has enough PP
        if trainer.pokemon_list[0].moves[move]["pp"] == 0:
            print(f"\n{trainer.pokemon_list[0].name} has no PP left for {move_name}! Choose another move.")
            continue

        # use the move against the enemy pokemon
        print()
        trainer.pokemon_list[0].use_move(move_name, enemy_pokemon)

        # check if the enemy pokemon has fainted
        if enemy_pokemon.base_stats['hp'] <= 0:
            print(f"\n{enemy_pokemon.name} has fainted! You win!")
            break

        # print the hp of the enemy pokemon
        print(f"{enemy_pokemon.name} HP: {enemy_pokemon.base_stats['hp']}")

        # update the round number
        round += 1
