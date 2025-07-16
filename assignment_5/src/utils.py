import os
import sys
import platform
import time
import ast
import pandas as pd

def clear_terminal():
    """
    Clears the terminal.
    """

    # clear the terminal based on the OS
    os.system("cls" if platform.system() == "Windows" else "clear")

def type_text(text, delay=0.03):
    """
    Prints the input text to the standard output by writing a character at each delay time.
    It makes the printed text more game-like.

    Parameters:
    - text: string with the text to be printed in the standard output.
    - delay: float representing the time in seconds to wait before printing the next character in the string.
    """

    # iterate through the characters in the input string
    for char in text:

        # write the character
        sys.stdout.write(char)

        # make the character immediately leave the buffer to be printed in the stdout
        sys.stdout.flush()

        # wait before the next iteration
        time.sleep(delay)

def choose_option(options, question_sentence="What do you want to do?"):
    """
    Makes the user choose among one of the items in the input list and returns the choice.

    Parameters:
    - options: list of strings with the names of the options to choose among to be displayed to the user.
    - question

    Returns:
    - choice_id: integer representing the index of the chosen option in the list options.
    """
    
    # question to be asked to the user
    type_text(f"\n{question_sentence}\n")

    # iterate while the user types a valid option
    while True:

        # make the use choose an option
        for i, option in enumerate(options):
            type_text(f"{i}: {option}\n")
        
        # check whether the option is valid
        no_int = False
        try:
            choice_id = int(input("> "))
        except ValueError:
            no_int = True
        if no_int or choice_id < 0 or choice_id >= len(options):
            type_text("\nInvalid choice. Please, choose one of the numbers displayed for the options:\n")
            continue
        
        # clear the terminal
        clear_terminal()

        # the option is valid
        return choice_id

def encode_types(dataset):
    """
    Encodes the pokemon types.
    Each type is one-hot encoded.
    Both the columns "player_types" and "opponent_types" are substituded by one column for each type in the dataset with value 1 if the considered pokemon has that type and 0 otherwise.

    Parameters:
    - dataset: pandas dataframe with pokemon data collected from a simulation run.
               It must have the columns "player_types" and "opponent_types".

    Returns:
    - pandas dataframe with the pokemon types encoded.
    """

    # transform the lists stored as strings into actual lists
    dataset["player_types"] = dataset["player_types"].apply(ast.literal_eval)
    dataset["opponent_types"] = dataset["opponent_types"].apply(ast.literal_eval)

    # encode players' types
    player_df = dataset.explode("player_types")
    player_df = pd.get_dummies(player_df["player_types"], prefix="player").groupby(player_df.index).sum()
    
    # encode opponents' types
    opponent_df = dataset.explode("opponent_types")
    opponent_df = pd.get_dummies(opponent_df["opponent_types"], prefix="opponent").groupby(opponent_df.index).sum()

    # remove the columns "player_types" and "opponent_types" and add the columns with players' types and opponents' types
    return pd.concat([dataset, player_df, opponent_df], axis=1).drop(["player_types", "opponent_types"], axis=1)
