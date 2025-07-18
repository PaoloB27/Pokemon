from pokemon_moves import moves
from pokemons import starter_pokemons, wild_pokemons
from game_engine import GameEngine

if __name__ == '__main__':

    # initialize the game
    game = GameEngine(starter_pokemons, wild_pokemons, moves)

    # run the game
    game.run_game()
