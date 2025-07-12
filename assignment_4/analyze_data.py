import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from simulations import load_moves, load_pokemons

def compute_hp_reductions(data):
    """
    Adds two new columns to the input DataFrame:
    - "Absolute HP Reduction %": % hps lost with respect to initial battle hps;
    - "Relative HP Reduction %": % hps lost during a single turn;

    Parameters:
    - data: pandas dataframe with the input data.

    Returns:
    - data: dataframe with new columns added.
    """
    
    # sort the dataframe
    data = data.sort_values(["Game", "Battle", "Turn"]).copy()

    # get the initial hps for each battle
    initial_hp = data.groupby(["Game", "Battle"])["Starter Initial HPs"].transform("first")

    # shift the hps up by 1 to get the hps at the end of each turn
    next_hp = data.groupby(["Game", "Battle"])["Starter Initial HPs"].shift(-1)

    # compute the percentage of lost hps at each turn with respect to the hps at the beginning of the battle
    data["Absolute HP Reduction %"] = (initial_hp - next_hp) / initial_hp * 100

    # compute the percentage of lost hps at each turn as the hps at the beginning of the turn minus the hps at the end of the turn
    data["Relative HP Reduction %"] = (data["Starter Initial HPs"] - next_hp) / data["Starter Initial HPs"] * 100

    # set the correct values for the last turn of each battle
    is_last_turn = data.groupby(["Game", "Battle"])["Turn"].transform("max") == data["Turn"]
    data.loc[is_last_turn, "Absolute HP Reduction %"] = 100 - data.loc[is_last_turn, "Residual HP"]
    data.loc[is_last_turn, "Relative HP Reduction %"] = (
        data.loc[is_last_turn, "Starter Initial HPs"] - data.loc[is_last_turn, "Residual HP"]
    ) / data.loc[is_last_turn, "Starter Initial HPs"] * 100

    return data

def simple_plot(data, save_path):
    """
    Plots the  average (± std dev) reduction of the percentage player's pokemon hps along the battle turns.

    Parameters:
    - data: pandas dataframe with data collected from the simulation.
    - save_path: path where to save the plot.
    """

    # compute the hp percentage reduction, both absolute and relative
    data = compute_hp_reductions(data)

    # create a single figure that will have both absolute and relative plots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    sns.set_style("whitegrid")

    # create the absolute plot
    sns.pointplot(data=data, x="Turn", y="Absolute HP Reduction %", errorbar="sd", ax=ax1, color="blue")
    ax1.set_title("Avg % of Initial HP Lost per Turn")
    ax1.set_ylabel("HP Reduction (%)")

    # create the relative plot
    sns.pointplot(data=data, x="Turn", y="Relative HP Reduction %", errorbar="sd", ax=ax2, color="red")
    ax2.set_title("Avg % of HP Lost per Turn")
    ax2.set_ylabel("HP Reduction (%)")

    # set some options and save
    plt.tight_layout()
    plt.savefig(save_path, dpi=350)
    plt.close()

def moves_pie_plots(data, save_dir):
    """
    For each starter pokemon, creates a figure with 2 pie plots:
    - the percentage of times each attack of the player's pokemon has been used;
    - the percentage of total damage done by each attack.

    Parameters:
    - data: pandas dataframe with data collected from the simulation.
    - save_dir: path to the directory where to save all the plots.
    """

    # number of times each attack of each starter pokemon has been used
    size_groups = data.groupby(["Starter Pokemon", "Starter Move"]).size().reset_index(name="Count")

    # total damage inflicted by each attack used by each starter pokemon
    move_damage = data.groupby(["Starter Pokemon", "Starter Move"])["Starter Damage Inflicted"].sum().reset_index(name="Total Move Damage")

    # iterate through the starter pokemons, so to create a different plot for each of them
    for starter in size_groups["Starter Pokemon"].unique():

        # dataframes with only the data related to the current starter pokemon
        curr_attack_df = size_groups[size_groups["Starter Pokemon"] == starter]
        curr_damage_df = move_damage[move_damage["Starter Pokemon"] == starter]

        # plot attack and damage percentage for the current starter pokemon
        fig, (ax_1, ax_2) = plt.subplots(1, 2, figsize=(10, 6))
        ax_1.pie(curr_attack_df["Count"], labels=curr_attack_df["Starter Move"], autopct="%1.1f%%")
        ax_2.pie(curr_damage_df["Total Move Damage"], labels=curr_damage_df["Starter Move"], autopct="%1.1f%%")
        ax_1.set_title(f"Moves Used by {starter.capitalize()}")
        ax_2.set_title(f"Damage Inflicted by the Moves Used by {starter.capitalize()}")
        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, f"{starter}_move_pie_plots.jpg"), dpi=350)
        plt.close()

def pokemon_types_pie_plot(simulation_data, pokemons, save_dir):
    """
    Creates a figure with two pie plots:
    - the distribution of the types of all the pokemons in the original dataset;
    - the distribution of the types of the pokemons encountered in the simulation.

    Parameters:
    - simulation_data: pandas dataframe with data collected from the simulation.
    - pokemons: pandas dataframe with all pokemons in the original dataset.
    - save_dir: path to the directory where to save all the plots.
    """

    # dataframe with names and types of the pokemons in the original dataset
    original_types = pokemons[["name", "types"]]

    # dataframe with names and types of the pokemons encountered in the simulation
    simulation_types = simulation_data["Wild Pokemon"].to_frame(name="name")
    simulation_types = simulation_types.merge(original_types, on="name", how="left")

    # count the number of occurrences of each type in two dataframes
    original_types = original_types.explode("types")["types"].value_counts(sort=False).sort_index()
    simulation_types = simulation_types.explode("types")["types"].value_counts(sort=False).sort_index()

    # plot the two series with counts
    fig, (ax_1, ax_2) = plt.subplots(1, 2, figsize=(16, 10))
    ax_1.pie(original_types.values, labels=original_types.index, labeldistance=1, rotatelabels=True)
    ax_2.pie(simulation_types.values, labels=simulation_types.index, labeldistance=1, rotatelabels=True)
    ax_1.set_title("Dataset Pokemon Types Distribution")
    ax_2.set_title("Simulation Pokemon Types Distribution")
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "types_pie_plots.jpg"), dpi=350)
    plt.close()

def damage_bar_plot(data, save_path):
    """
    For each starter pokemon, it plots the average damage inflicted, grouped by level.

    Parameters:
    - data: pandas dataframe with data collected from the simulation.
    - save_path: path to the file where to save a single figure with all the plots.
    """

    # compute the average damage inflicted by each starter pokemon grouped by level
    plot_data = data.groupby(["Starter Pokemon", "Starter Level"])["Starter Damage Inflicted"].mean().reset_index(name="Mean Damage Inflicted")
    
    # create a facet plot with the bar plot for each starter pokemon in a different subplot
    sns.set_style("whitegrid")
    g = sns.FacetGrid(plot_data, col="Starter Pokemon", height=5, aspect=1.5)
    g.map(sns.barplot, "Starter Level", "Mean Damage Inflicted", order=sorted(plot_data["Starter Level"].unique()))
    plt.tight_layout()
    plt.savefig(save_path, dpi=350)
    plt.close()

def wins_image_plot(data, pokemons, save_dir):
    """
    For each starter pokemon, it plots the percentage of wins in function of the wild pokemon's level and types.

    Parameters:
    - data: pandas dataframe with data collected from the simulation.
    - pokemons: pandas dataframe with the original dataset of pokemons.
    - save_dir: path to the folder where to save a plot for each starter pokemon.
    """

    # add a column to the input dataframe with the types of the wild pokemons encountered
    plot_data = data.copy()
    plot_data = plot_data.rename(columns={"Wild Pokemon": "name"})
    plot_data = plot_data.merge(pokemons[["name", "types"]], on="name", how="left")

    # compute the percentage of wins in function of the wild pokemon's level and types
    plot_data = plot_data.explode("types")
    plot_data = plot_data.groupby(["Starter Pokemon", "types", "Wild Level"])["Battle Outcome"].mean().reset_index(name="Percentage Wins")
    plot_data["Percentage Wins"] = plot_data["Percentage Wins"] * 100

    # create and save a different plot for each starter pokemon
    starters = plot_data["Starter Pokemon"].unique()
    for starter in starters:
        subset = plot_data[plot_data["Starter Pokemon"] == starter]
        heatmap_data = subset.pivot(index="types", columns="Wild Level", values="Percentage Wins")
        plt.figure(figsize=(12, 6))
        plt.grid(visible=False)
        plt.imshow(heatmap_data)
        plt.hot()
        plt.colorbar()
        plt.title(f"Percentage of Wins {starter.capitalize()}")
        plt.xlabel("Wild Pokemon Level")
        plt.ylabel("Wild Pokemon Type")
        plt.xticks(ticks=range(len(heatmap_data.columns)), labels=heatmap_data.columns)
        plt.yticks(ticks=range(len(heatmap_data.index)), labels=heatmap_data.index)
        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, f"{starter}_wins_image_plot.jpg"), dpi=350)
        plt.close()

def parse_args():
    """
    Parses command line arguments.

    Returns:
    - parser.parse_args(): ArgumentParser object with parsed arguments.
    """

    # create the argument parser
    parser = argparse.ArgumentParser(description="Creates some plots, taking as input the data generated by the simulation.")

    # arguments
    parser.add_argument("-i", "--input_data", type=str, required=False, default=os.path.join("results", "collected_data.csv"), help="Path to the file with the collected data.")
    parser.add_argument("-o", "--output_dir", type=str, required=False, default=os.path.join("results"), help="Path to the folder where to save the plots.")
    parser.add_argument("--moves", type=str, required=False, default=os.path.join("..", "data", "moves.json"), help="Path to the file with pokemon moves.")
    parser.add_argument("--pokemons", type=str, required=False, default=os.path.join("..", "data", "pokemons.json"), help="Path to the file with all pokemons.")
                          
    return parser.parse_args()

if __name__ == '__main__':

    # parse command line arguments
    args = parse_args()

    # load data
    simulation_data = pd.read_csv(args.input_data)
    pokemons = load_pokemons(args.pokemons, load_moves(args.moves))

    # create the output folder, if it does not exist
    os.makedirs(args.output_dir, exist_ok=True)

    # make some plots
    simple_plot(simulation_data, os.path.join(args.output_dir, "simple_plot.jpg"))
    moves_pie_plots(simulation_data, args.output_dir)
    pokemon_types_pie_plot(simulation_data, pokemons, args.output_dir)
    damage_bar_plot(simulation_data, os.path.join(args.output_dir, "damage_bar_plots.jpg"))
    wins_image_plot(simulation_data, pokemons, args.output_dir)