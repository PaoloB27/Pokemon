import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def compute_hp_reduction_initial_hps(data):
    """
    Computes the percentage reduction of hps at each turn with respect to the hps of the starter pokemon at the beginning of the battle.

    Parameters:
    - data: pandas dataframe with data related to a single battle of a single game.

    Returns:
    - data: pandas series with the reduction of hps at each turn in the column "HP Reduction %".
    """

    # sort the values by increasing turn
    red_data = data.sort_values("Turn")

    # hps of the starter pokemon at the beginning of the battle
    initial_hps = red_data.iloc[0]["Starter Initial HPs"]

    # shift the initial hps up by 1: shifted_hps has the hps after the end of a turn
    shifted_hps = red_data["Starter Initial HPs"].shift(-1)

    # compute the percentage reduction of hps with respect to hps of the beginning of the battle
    red_data["HP Reduction %"] = (initial_hps - shifted_hps) / initial_hps * 100

    # set the hp reduction in the final turn to 100 - final residual hps
    red_data.at[red_data.index[-1], "HP Reduction %"] = 100 - red_data.iloc[-1]["Residual HP"]

    return red_data

def compute_hp_reduction_relative(data):
    """
    Computes the percentage reduction of hps at the end of each turn with respect to the hps of the beginning of the turn.

    Parameters:
    - data: pandas dataframe with data related to a single battle of a single game.

    Returns:
    - data: pandas series with the reduction of hps at each turn in the column "HP Reduction %".
    """

    # sort the values by increasing turn
    red_data = data.sort_values("Turn")

    # shift the initial hps up by 1: shifted_hps has the hps after the end of a turn
    shifted_hps = red_data["Starter Initial HPs"].shift(-1)

    # compute the percentage reduction of hps in each turn as (hps at the end of the turn - hps at the beginning of the turn)
    red_data["HP Reduction %"] = (red_data["Starter Initial HPs"] - shifted_hps) / red_data["Starter Initial HPs"] * 100

    # set the hp reduction in the final turn
    red_data.at[red_data.index[-1], "HP Reduction %"] = red_data.iloc[-1]["Starter Initial HPs"] - red_data.iloc[-1]["Residual HP"]

    return red_data

def simple_plot(data, save_path):
    """
    Plots the  average (± std dev) reduction of the percentage player's pokemon hps along the battle turns.

    Parameters:
    - data: pandas dataframe with data collected from the simulation.
    - save_path: path where to save the plot.
    """

    # compute the hp percentage reduction, both absolute and relative
    absolute_df = data.groupby(["Game", "Battle"]).apply(compute_hp_reduction_initial_hps, include_groups=False)
    relative_df = data.groupby(["Game", "Battle"]).apply(compute_hp_reduction_relative, include_groups=False)

    # plot the hp percentage reduction, both relative and absolute
    fig, (ax_1, ax_2) = plt.subplots(1, 2, figsize=(10, 6))
    sns.set_style("whitegrid")
    
    sns.pointplot(data=absolute_df, x="Turn", y="HP Reduction %", errorbar="sd", ax=ax_1, color="b")
    ax_1.set_title("Average Percentage of Initial HPs Lost Across Turns")
    ax_1.set_xlabel("% Initial HP Reduction")
    
    sns.pointplot(data=relative_df, x="Turn", y="HP Reduction %", errorbar="sd", ax=ax_2, color="r")
    ax_2.set_title("Average Percentage of HPs Lost Across Turns")
    ax_2.set_xlabel("% Relative HP Reduction")
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=350)
    plt.close()

def turn_distribution_plot(data, save_path):
    """
    It plots the distribution of the number of turns in the battles.

    Parameters:
    - data: pandas dataframe with data collected from the simulation.
    - save_path: path where to save the plot.
    """

    # plot the turn distribution
    sns.set_style("whitegrid")
    ax = sns.boxplot(data=data, y="Battle Turns", zorder=1, color=sns.xkcd_rgb["powder blue"])

    # compute mean, median, 25th and 75th quantiles
    mean = data["Battle Turns"].mean()
    median = data["Battle Turns"].median()
    q_1 = data["Battle Turns"].quantile(0.25)
    q_3 = data["Battle Turns"].quantile(0.75)

    # print the statistics
    print("\nTurns Statistics")
    print(f"Mean: {mean: .2f}")
    print(f"Median: {median: .2f}")
    print(f"Q1: {q_1: .2f}")
    print(f"Q3: {q_3: .2f}")

    # plot the computed statistics
    ax.scatter(0, median, color="orange", marker="d", label="Median", zorder=2)
    ax.scatter(0, mean, color="red", marker="o", label="Mean", zorder=3)
    ax.scatter(0, q_1, color="blue", marker="^", label="Q1", zorder=4)
    ax.scatter(0, q_3, color="green", marker="v", label="Q3", zorder=5)

    # plot options
    plt.legend()
    plt.title("Distribution of Number of Turns")
    plt.ylabel("Number of Turns")
    plt.savefig(save_path, dpi=350)
    plt.close()

def hp_distribution_plot(data, save_path):
    """
    It plots the distribution of the residual hp ay the end of the battles.

    Parameters:
    - data: pandas dataframe with data collected from the simulation.
    - save_path: path where to save the plot.
    """

    # plot the turn distribution
    sns.set_style("whitegrid")
    ax = sns.boxplot(data=data, y="Residual HP", zorder=1, color=sns.xkcd_rgb["powder blue"])

    # compute mean, median, 25th and 75th quantiles
    mean = data["Residual HP"].mean()
    median = data["Residual HP"].median()
    q_1 = data["Residual HP"].quantile(0.25)
    q_3 = data["Residual HP"].quantile(0.75)

    # print the statistics
    print("\nResidual HP Statistics")
    print(f"Mean: {mean: .2f}%")
    print(f"Median: {median: .2f}%")
    print(f"Q1: {q_1: .2f}%")
    print(f"Q3: {q_3: .2f}%")

    # plot the computed statistics
    ax.scatter(0, median, color="orange", marker="d", label="Median", zorder=2)
    ax.scatter(0, mean, color="red", marker="o", label="Mean", zorder=3)
    ax.scatter(0, q_1, color="blue", marker="^", label="Q1", zorder=4)
    ax.scatter(0, q_3, color="green", marker="v", label="Q3", zorder=5)


    plt.title("Distribution Residual HPs")
    plt.ylabel("Residual HPs")
    plt.savefig(save_path, dpi=350)
    plt.close()

def stats_per_enemy_plot(data, save_dir):
    """
    For each starter pokemon, it plots the percentage of won battles against each different enemy, 
    the mean residual HPs and the standard deviation.

    Parameters:
    - data: pandas dataframe with data collected from the simulation.
    - save_dir: path to the directory where to save the plots.
    """

    # convert "Battle Outcome" from boolean to 0/100 scale, because we will compute percentages afterwards
    data["Battle Outcome"] = data["Battle Outcome"].astype(int).mul(100)

    # compute the median number of turns
    median_turns = data["Battle Turns"].median()

    # create a plot for each starter pokemon
    for starter_pokemon in data["Starter Pokemon"].unique():
        
        # extract the data related to the current starter pokemon
        curr_df = data[data["Starter Pokemon"] == starter_pokemon]

        # compute the mean cumulative outcome and the mean residual hps and standard deviation for each wild pokemon
        agg_df = curr_df.groupby("Wild Pokemon").agg({"Battle Outcome": "mean", "Residual HP": ["mean", "std"], "Battle Turns": "mean"})

        # set the column names
        agg_df.columns = ["Mean Wins", "Mean Residual HPs", "Std Residual HPs", "Mean Turns"]
        agg_df = agg_df.reset_index()

        # add columns "Novice" and "Skilled" with boolean values for each wild pokemon
        agg_df["Novice"] = agg_df["Mean Wins"].between(70, 90) & (agg_df["Mean Residual HPs"] > 70)
        agg_df["Skilled"] = agg_df["Mean Wins"].between(50, 70) & (agg_df["Mean Turns"] > median_turns)

        # sort the dataframe by mean wins
        agg_df = agg_df.sort_values("Mean Wins", ascending=True).reset_index(drop=True)

        # define the position on the y-axis for the names of the wild pokemons
        wild_pokemons = agg_df["Wild Pokemon"]
        y_positions = list(range(len(wild_pokemons)))
        
        # thickness of the bars
        bar_height = 0.4

        # create the figure
        fig, ax = plt.subplots(figsize=(10, len(wild_pokemons) * 0.2))
        ax.grid(axis='x', linestyle='-', alpha=0.7, zorder=1)
        ax.set_title(f"Percentage of Wins and Residual HPs of {starter_pokemon.capitalize()} Against Each Encountered Wild Pokemon")
        ax.set_xlabel("Percentage")
        ax.set_ylabel("Wild Pokemon")

        # plot wins bars
        ax.barh([y + bar_height / 2 for y in y_positions],
                agg_df["Mean Wins"],
                height=bar_height,
                color="skyblue",
                label="% Wins",
                zorder=2
        )

        # plot hps bars
        ax.barh([y - bar_height / 2 for y in y_positions],
                agg_df["Mean Residual HPs"],
                height=bar_height,
                color="salmon",
                label="% Residual HPs",
                zorder=2
        )

        # plot error bars only for the hps bars
        ax.errorbar(x=agg_df["Mean Residual HPs"],
                    y=[y - bar_height / 2 for y in y_positions],
                    xerr=agg_df["Std Residual HPs"],
                    fmt="none",
                    ecolor="black",
                    capsize=2,
                    zorder=3
        )
        
        # highlight Novice and Skilled pokemon in the plot
        novice_plotted = False
        skilled_plotted = False
        for i, row in agg_df.iterrows():
            if row["Novice"]:
                ax.scatter(-20, y_positions[i],
                    marker="o",
                    color="blue",
                    s=50,
                    label="Novice User" if not novice_plotted else "",
                    zorder=4
                )
                novice_plotted = True
            elif row["Skilled"]:
                ax.scatter(-20, y_positions[i],
                    marker="*",
                    color="red",
                    s=50,
                    label="Skilled User" if not skilled_plotted else "",
                    zorder=4
                )
                skilled_plotted = True

        # set other plot options and save the figure
        ax.set_yticks(y_positions, wild_pokemons)
        ax.set_xlim(-21, 101)
        ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, f"{starter_pokemon}_stats_per_enemy.jpg"), dpi=350)
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
                          
    return parser.parse_args()

if __name__ == '__main__':

    # parse command line arguments
    args = parse_args()

    # load data
    simulation_data = pd.read_csv(args.input_data)

    # create the output folder, if it does not exist
    os.makedirs(args.output_dir, exist_ok=True)

    # make some plots
    simple_plot(simulation_data, os.path.join(args.output_dir, "simple_plot.jpg"))
    # turn_distribution_plot(simulation_data, os.path.join(args.output_dir, "turns_distribution_plot.jpg"))
    # hp_distribution_plot(simulation_data, os.path.join(args.output_dir, "hp_distribution_plot.jpg"))
    # stats_per_enemy_plot(simulation_data, args.output_dir)