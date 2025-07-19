import os
import random
import argparse
from simulation import Simulation

def parse_args():
    """
    Parses command line arguments.

    Returns:
    - parser.parse_args(): ArgumentParser object with parsed arguments.
    """

    # create the argument parser
    parser = argparse.ArgumentParser(description="Runs a simulation with random battles, collecting and saving data.")

    # arguments
    parser.add_argument("--n_games", type=int, required=False, default=1000, help="Number of games to run.")
    parser.add_argument("--n_battles", type=int, required=False, default=500, help="Number of battles to run in each game.")
    parser.add_argument("--input_pokemons", type=str, required=False, default=os.path.join("..", "data", "pokemons.json"), help="Path to the dataset with pokemons.")
    parser.add_argument("--input_moves", type=str, required=False, default=os.path.join("..", "data", "moves.json"), help="Path to the dataset with moves.")
    parser.add_argument("--input_type_effectiveness", type=str, required=False, default=os.path.join("..", "data", "type_effectiveness.json"), help="Path to the dataset with type effectiveness pairs.")
    parser.add_argument("--output_data", type=str, required=False, default=os.path.join("..", "results", "collected_data.csv"), help="Path to the file where to save the collected data.")
    parser.add_argument("--random_seed", type=int, required=False, default=27, help="Random seed for reproducibility.")    

    return parser.parse_args()

if __name__ == '__main__':

    # parse command line arguments
    args = parse_args()

    # set a random seed for reproducibility
    random.seed(args.random_seed)

    # initialize a Simulation object
    simulation = Simulation(args.n_games, args.n_battles, args.input_pokemons, args.input_moves, args.input_type_effectiveness)

    # run the simulation
    simulation.run_simulation()

    # save simulation data
    simulation.save_data(args.output_data)
