import os
import pickle
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def simple_plot(data, save_path):
    """
    For each starter pokemon, it plots the cumulative number of battle wins at each game, averaged by the number of games.

    Parameters:
    - data: pandas dataframe with data collected from the simulation.
    - save_path: path where to save the plot.
    """

    # convert boolean values in the "Battle Outcome" column into integers
    data["Battle Outcome"] = data["Battle Outcome"].astype(int)

    # compute the cumulative number of battle won in a game, for each starter pokemon
    plot_df = data.groupby(by=["Starter Pokemon", "Game"])["Battle Outcome"].sum()

    # compute the average of the cumulative number of wins across games, for each starter pokemon
    plot_df = plot_df.groupby(by=["Starter Pokemon"]).mean()

    # convert the series into a dataframe
    plot_df = plot_df.reset_index()
    plot_df.columns = ["Starter Pokemon", "Average Wins"]
    
    # plot the values
    sns.set_style("whitegrid")
    ax = sns.barplot(data=plot_df, x="Starter Pokemon", y="Average Wins")


    # add the values on top of each bar
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f', label_type='edge', padding=1)

    # plot settings
    plt.title(f"Number of Wins in {data["Battle"].max()} Battles Averaged over {data["Game"].max()} Games")
    plt.ylabel("Average Wins")
    plt.xlabel("Starter Pokemon")
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
    parser.add_argument("-i", "--input_data", type=str, required=False, default=os.path.join("results", "collected_data.pickle"), help="Path to the file with the collected data.")
    parser.add_argument("-o", "--output_dir", type=str, required=False, default=os.path.join("results"), help="Path to the folder where to save the plots.")
                          
    return parser.parse_args()

if __name__ == '__main__':

    # parse command line arguments
    args = parse_args()

    # load data
    pickle_in = open(args.input_data,"rb")
    simulation_data = pickle.load(pickle_in)
    pickle_in.close()

    # create the output folder, if it does not exist
    os.makedirs(args.output_dir, exist_ok=True)

    # convert the list of dictionaries into a pandas dataframe
    simulation_data = pd.DataFrame(simulation_data)

    # make some plots
    # simple_plot(simulation_data, os.path.join(args.output_dir, "simple_plot.jpg"))
    # turn_distribution_plot(simulation_data, os.path.join(args.output_dir, "turns_distribution_plot.jpg"))
    # hp_distribution_plot(simulation_data, os.path.join(args.output_dir, "hp_distribution_plot.jpg"))
    stats_per_enemy_plot(simulation_data, args.output_dir)