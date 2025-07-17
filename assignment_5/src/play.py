import os
import argparse
from game_engine import GameEngine

def parse_args():
    """
    Parses command line arguments.

    Returns:
    - parser.parse_args(): ArgumentParser object with parsed arguments.
    """

    # create the argument parser
    parser = argparse.ArgumentParser(description="Runs the game.")

    # arguments
    parser.add_argument("--pokemons", type=str, required=False, default=os.path.join("..", "data", "pokemons.json"), help="Path to the dataset with pokemons.")
    parser.add_argument("--moves", type=str, required=False, default=os.path.join("..", "data", "moves.json"), help="Path to the dataset with moves.")
    parser.add_argument("--type_effectiveness", type=str, required=False, default=os.path.join("..", "data", "type_effectiveness.json"), help="Path to the dataset with type effectiveness pairs.")
    parser.add_argument("--recommender", type=str, required=False, default=os.path.join("..", "model", "model.pickle"), help="Path to the model to use as recommendation system.")
                          
    return parser.parse_args()


if __name__ == '__main__':

    # parse command line arguments
    args = parse_args()

    # initialize the game
    game = GameEngine(args.pokemons, args.moves, args.type_effectiveness, args.recommender)

    # run the game
    game.run()
