from pokemons_and_moves import starter_pokemons, moves
from simple_game import SimpleGame

if __name__ == '__main__':

    # initialize the game
    game = SimpleGame(starter_pokemons, moves)

    # run the battle
    game.battle()