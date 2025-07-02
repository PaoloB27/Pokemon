from game_engine import initialize_pokemon_trainer, run_game

# main function that runs the script
if __name__ == '__main__':

    # initialize the pokemon trainer with the information provided by the user
    trainer = initialize_pokemon_trainer()

    # run the game
    run_game(trainer)
