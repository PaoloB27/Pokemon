import os
import json
import pickle
import random
import pandas as pd
from pokemon_trainer import PokemonTrainer
from pokemon_character import PokemonCharacter
from utils import clear_terminal, type_text, choose_option

class GameEngine():
    
    # set the maximum level that can be achieved by a pokemon in the game
    max_level_game = 25

    # folder where to load and save game data
    savings_folder = os.path.join("..", "saved_games")

    def __init__(self, pokemons_path, moves_path, type_effectiveness_path, recommender_path, starter_names=["bulbasaur", "charmander", "squirtle"]):
        """
        A GameEngine object has everything needed for playing the game.
        It asks the user whether to load previously saved data, if any.

        Parameters:
        - pokemons_path: path to the dataset with all the pokemons available in the game.
        - moves_path: path to the dataset with all the moves available in the game.
        - type_effectiveness_path: path to the dataset with effectiveness for all possible pairs of types.
        - recommender_path: path to the trained predictor that is capable of predicting the outcome of a battle given the types and the active statistics of the pokemons involved.
        - starter_names: list of strings with the names of the starter pokemons.
        """

        # load moves, pokemons and type effectiveness data into pandas dataframes
        type_text("\nStarting the game...\n")
        self.moves = self.load_moves(moves_path)
        self.pokemons = self.load_pokemons(pokemons_path, self.moves)
        self.type_effectiveness = self.load_type_effectiveness(type_effectiveness_path)

        # load the recommender
        with open(recommender_path, "rb") as file:
            self.recommender = pickle.load(file)

        # initialize the pokemon trainer
        clear_terminal()
        self.pokemon_trainer = self.initialize_pokemon_trainer(starter_names)

    @staticmethod
    def to_pokemon_character(row_df):
        """
        Converts the row of a dataframe with pokemon information into a PokemonCharacter object.

        Parameters:
        - row_df: row of a pandas dataframe with all information about a pokemon.

        Returns:
        - pokemon: PokemonCharacter with all information in the input row about a pokemon.
        """

        # instantiate a PokemonCharacter object with the input information
        pokemon = PokemonCharacter(
            name=row_df["name"],
            base_stats=row_df["baseStats"],
            moves=row_df["moves"],
            national_pokedex_number=row_df["national_pokedex_number"],
            types=row_df["types"],
            level=row_df["level"]
        )

        # return the PokemonCharacter object
        return pokemon

    @staticmethod
    def load_moves(path):
        """
        Loads a dataset of moves from a .json file.
        It removes the moves with "power" equal to null and the keys "effect", "effects", "changes".

        Parameters:
        - path: path to the .json file with the moves to be loaded.

        Returns:
        - moves: pandas dataframe with each entry that is a different move.
        """

        # keys to be removes
        keys_to_remove = ["effect", "effects", "changes"]

        # initialize the list of dictionaries that will contain the loaded moves
        moves = []

        # open the .json file
        with open(path, "r") as file:
            
            # iterate through lines
            for line in file:

                # convert the string into a dictionary
                move = json.loads(line)

                # add the move only if the value of "power" and "accuracy" are not None
                if move["power"] is not None and move["accuracy"] is not None:
                    
                    # remove the entries with key in keys_to_remove
                    move = {key: value for key, value in move.items() if key not in keys_to_remove}

                    # add the dictionary repesenting a move to the list
                    moves.append(move)

        # return the loaded moves in a pandas dataframe
        return pd.DataFrame(moves)

    @staticmethod
    def load_pokemons(path, moves):
        """
        Loads a dataset of pokemons from a .json file.
        It adds the entry with key "level" and value 1 to each dictionary representing a pokemon.
        It also adds two moves to each pokemon by sampling them at random from the input moves such that type coherence is respected.

        Parameters:
        - path: path to the .json file with the pokemons to be loaded.
        - moves: pandas dataframe with all possible pokemon moves.

        Returns:
        - pokemons: dataframe with each entry that represents a different pokemon.
        """

        # initialize the list that will contain the loaded pokemons
        pokemons = []

        # open the .json file
        with open(path, "r") as file:
            
            # iterate through lines
            for line in file:

                # convert the line into a dictionary representing a pokemon
                curr_pokemon = json.loads(line)

                # add the entry ("level", 1)
                curr_pokemon["level"] = 1

                # add to the loaded pokemon 4 moves sampled uniformly at random such that the pokemon has at least one move of each type of the pokemon itself
                n_moves = 4
                curr_pokemon["moves"] = []
                for pokemon_type in curr_pokemon["types"]:
                    if pokemon_type in moves["type"].explode().unique():                                                                                                   # there are no moves of some pokemon types in the dataset
                        curr_pokemon["moves"].extend(moves[moves["type"] == pokemon_type].sample(random_state=random.randint(0, 10000)).to_dict(orient="records"))
                curr_pokemon["moves"].extend(moves[(moves["type"] == "normal") | (moves["type"].isin(curr_pokemon["types"]))].sample(n=n_moves - len(curr_pokemon["moves"]), random_state=random.randint(0, 10000)).to_dict(orient="records"))

                # append the current pokemon to the list of pokemons
                pokemons.append(curr_pokemon)

        # return the loaded pokemons as a pandas dataframe
        return pd.DataFrame(pokemons)

    @staticmethod
    def load_type_effectiveness(path):
        """
        Loads type effectiveness relations from a .json file.

        Parameters:
        - path: path to the .json file with the data to be loaded.

        Returns:
        - data: pandas dataframe with the input data. Each row is a different (attack_type, defend_type) pair.
        """

        # initialize the list that will contain the loaded data
        data = []

        # open the .json file
        with open(path, "r") as file:
            
            # iterate through lines
            for line in file:

                # convert the line into a dictionary
                pair = json.loads(line)

                # append the pair to the list
                data.append(pair)

        # return the loaded type effectivenesses after having converted them into a pandas dataframe
        return pd.DataFrame(data)

    def initialize_pokemon_trainer(self, starter_names):
        """
        Initializes a PokemonTrainer loading existing data or creating a new instance.

        Parameters:
        - starter_names: list of strings with the names of the starter pokemons.

        Returns:
        - trainer: PokemonTrainer object representing the initialized pokemon trainer.
        """

        # find all saved games, if any
        saved_games = ["Start a new game"]
        if os.path.isdir(self.savings_folder):
            saved_games.extend(os.listdir(self.savings_folder))

        # ask the user to choose whether to create a new character or load an existing one
        choice = choose_option([saved_games[0]] + [f"Load {saved_games[i][:-len(".pickle")]} data" for i in range(1, len(saved_games))], "Welcome to the game! What do you want to do?")
        clear_terminal()

        # load the file chosen by the user and return the corresponding PokemonTrainer object
        if choice > 0:
            with open(os.path.join(self.savings_folder, saved_games[choice]), "rb") as file:
                trainer = pickle.load(file)
            type_text(f"\nHello {trainer.name}! Welcome back to the Pokemon World!\n")
            return trainer
        
        # ask the user (i.e., the pokemon trainer) to enter his name
        type_text("\nLet's start a new game then! What is your name?\n")
        trainer_name = input("> ")
        clear_terminal()
        
        # create the pokemon trainer
        trainer = PokemonTrainer(trainer_name)

        # make the user choose the starter pokemon
        starter_pokemon_choice = choose_option([name.capitalize() for name in starter_names], f"Ok {trainer_name}, I want you to choose one of the following pokemons:")
        clear_terminal()

        # create the starter pokemon with a random level between 5 and 15 and add it to the pokemon trainer's list
        chosen_pokemon_name = starter_names[int(starter_pokemon_choice)]
        chosen_pokemon = self.pokemons[self.pokemons["name"] == chosen_pokemon_name].iloc[0]
        chosen_pokemon["level"] = random.randint(5, 15)
        chosen_pokemon = self.to_pokemon_character(chosen_pokemon)
        type_text(f"You chose {chosen_pokemon.name.capitalize()}! Great choice {trainer_name}!\n\n")
        trainer.add_pokemon(chosen_pokemon)

        # add 10 potions and 10 pokeballs to the pokemon trainer's items
        trainer.add_items("potion", 10)
        trainer.add_items("pokeball", 10)

        return trainer

    def attack(self, opponent_pokemon):
        """
        The active pokemon of the pokemon trainer attacks the opponent pokemon.

        Parameters:
        - opponent_pokemon: PokemonCharacter object representing the pokemon that receives the attack.

        Returns:
        - is_defeated: boolean indicating whether the opponent pokemon is defeated or not.
        """

        # if the active pokemon does not have any move with pps > 0, then return
        if not [pp for pp in self.pokemon_trainer.active_pokemon.curr_pps.values() if pp > 0]:
            type_text(f"\nOh no! {self.pokemon_trainer.active_pokemon.name.capitalize()} finished all the PPs!\n")
            return False

        # make the pokemon trainer choose a move that still has some pps
        possible_moves = [move_name for move_name, pp in self.pokemon_trainer.active_pokemon.curr_pps.items() if pp > 0]
        options = [f"{move_name} | {int(pp)} PP" for move_name, pp in self.pokemon_trainer.active_pokemon.curr_pps.items() if pp > 0]
        chosen_move = possible_moves[choose_option(options, question_sentence=f"Which move do you want {self.pokemon_trainer.active_pokemon.name.capitalize()} to use?")]

        # make the active pokemon attack the opponent pokemon with the chosen move
        self.pokemon_trainer.active_pokemon.use_move(chosen_move, opponent_pokemon, self.type_effectiveness)

        # check whether the opponent pokemon is defeated and end the battle in this case
        if opponent_pokemon.curr_hp <= 0:
            type_text(f"\nCongratulations! The wild {opponent_pokemon.name.capitalize()} is defeated!\n")
            return True
        
        # the opponent pokemon is not difeated
        return False

    def use_item(self, opponent_pokemon):
        """
        Makes the pokemon trainer choose an item among the available ones and applies it.

        Parameters:
        - opponent_pokemon: PokemonCharacter object representing the opponent pokemon in the battle.

        Returns:
        - is_catched: boolean indicating whether the opponent pokemon is catched or not, in case the item to use is a pokeball.
                    If the item to use is not a pokeball, then it returns False.
        """

        # make the trainer choose which item has to be used
        items = [item_name for item_name in self.pokemon_trainer.items.keys()]
        options = [f"{item_name} | {quantity}" for item_name, quantity in self.pokemon_trainer.items.items()]
        chosen_item = items[choose_option(options, "What item do you want to use?")]

        # apply a potion to the pokemon trainer's active pokemon
        if chosen_item == "potion":
            self.pokemon_trainer.use_potion()
            return False
        
        # use a pokeball to try to catch the opponent pokemon
        elif chosen_item == "pokeball":
            
            # there is space for a new pokemon in the trainer's list
            try:
                
                # the pokemon has been catched
                if self.pokemon_trainer.use_pokeball(opponent_pokemon):
                    return True
                
                # the pokemon has not been catched
                return False
            
            # there is not space for a new pokemon in the trainer's list, but the pokemon has been catched and freed, so the battle ends
            except OverflowError:
                type_text(f"The catched {opponent_pokemon.name.capitalize()} is left free and the used pokeball is thrown away.\n")
                return True

    def run_away(self, opponent_pokemon):
        """
        Makes the pokemon trainer try to run away from the encountered wild pokemon.

        Parameters:
        - opponent_pokemon: PokemonCharacter object representing the opponent pokemon in the battle.

        Returns:
        - is_escaped: boolean indicating whether the pokemon trainer has run away or not.
        """

        # print some information
        type_text(f"{self.pokemon_trainer.name.capitalize()} wants to run away.\n")

        # probability of running away
        run_prob = 0.6

        # the pokemon trainer successfully runs away, so the battle is over
        if random.random() < run_prob:
            type_text(f"{self.pokemon_trainer.name.capitalize()} runs away, the battle is over.\n")
            return True
        
        # the pokemon trainer fails to run away, so the battle goes on
        type_text(f"{opponent_pokemon.name.capitalize()} prevents {self.pokemon_trainer.name.capitalize()} to run away, the battle continues!\n")
        return False

    def change_pokemon(self):
        """
        Changes the active pokemon during a battle.

        Returns:
        - True if the change has been successful, False if the change cannot be made.
        """

        # pokemon that can be selected for the change
        available_pokemon = [pokemon.name for pokemon in self.pokemon_trainer.pokemon_list if pokemon is not self.pokemon_trainer.active_pokemon and pokemon.curr_hp > 0]
        available_pokemon_to_display = [f"{pokemon.name} | {pokemon.curr_hp} HP" for pokemon in self.pokemon_trainer.pokemon_list if pokemon is not self.pokemon_trainer.active_pokemon and pokemon.curr_hp > 0]
        
        # there is at least a pokemon that can be used
        if available_pokemon:
            chosen_pokemon = available_pokemon[choose_option(available_pokemon_to_display, "What pokemon do you want to become active?")]
            self.pokemon_trainer.change_active_pokemon(chosen_pokemon)
            return True
        
        # there is no pokemon that can be used
        type_text(f"You cannot change {self.pokemon_trainer.active_pokemon.name.capitalize()}!\n")
        return False

    def opponent_pokemon_turn(self, opponent_pokemon):
        """
        Makes the opponent pokemon attack the active pokemon of the trainer.
        If the trainer's active pokemon is defeated, then a new active pokemon is chosen in the trainer's list, if any.
        If there is no pokemon in the trainer's list that is not K.O., then True is returned.

        Parameters:
        - opponent_pokemon: PokemonCharacter object representing the opponent pokemon in the battle.

        Returns:
        - is_defeated: boolean indicating whether all pokemon of the pokemon trainer have been defeated or not.
        """

        # print some information    
        type_text(f"\nIt's the turn of {opponent_pokemon.name.capitalize()} now!\n\n")

        # if the wild pokemon does not have any move with pp > 0, then return
        if not [pp for pp in opponent_pokemon.curr_pps.values() if pp > 0]:
            type_text(f"\nOh no! {opponent_pokemon.name.capitalize()} finished all the PPs!\n")
            return False

        # make the opponent pokemon attack the trainer's active pokemon with a move sampled uniformly at random among the available ones
        opponent_pokemon.use_move(random.choice([move_name for move_name, pp in opponent_pokemon.curr_pps.items() if pp > 0]), self.pokemon_trainer.active_pokemon, self.type_effectiveness)
        
        # check whether the trainer's active pokemon is defeated
        if self.pokemon_trainer.active_pokemon.curr_hp <= 0:
            
            # print some information
            type_text(f"\n{self.pokemon_trainer.active_pokemon.name.capitalize()} is defeated!\n")

            # if all trainer's pokemon are defeated, then the battle ends and the pokemon trainer has to go to the pokemon center
            if not self.change_pokemon():
                type_text(f"\nAll {self.pokemon_trainer.name}'s pokemon are K.O., so {self.pokemon_trainer.name} loses the battle!\n")
                return True
        
        # the battle is not ended
        return False

    def check_pps(self, opponent_pokemon):
        """
        Checks whether all trainer's pokemons and the opponent pokemon do not have any move with pp > 0.

        Parameters:
        - opponent_pokemon: PokemonCharacter object representing the opponent pokemon in the battle.

        Returns:
        - no_pps: boolean indicating whether all trainer's pokemons and the opponent pokemon do not have any move with pp > 0.
        """

        # check whether the opponent pokemon has at least a move with pp > 0
        for pp in opponent_pokemon.curr_pps.values():
            if pp > 0:
                return False
        
        # check whether there is at least one trainer's pokemon that can fight with at least one move with pp > 0
        for pokemon in self.pokemon_trainer.pokemon_list:
            if pokemon.curr_hp > 0:
                for pp in opponent_pokemon.curr_pps.values():
                    if pp > 0:
                        return False
                
        # no pokemon has at least one move with pp > 0
        type_text(f"\n{self.pokemon_trainer.name} has no pokemon with pp > 0 that can fight!\n")
        type_text(f"Even {opponent_pokemon.name.capitalize()} has no move with pp > 0!\n")
        type_text(f"The battle ends.\n")
        return True

    def get_features(self, player_pokemon, opponent_pokemon):
        """
        """

        # create a datafram with the information about the two pokemons
        X_pokemon = pd.DataFrame(
            [{
                "player_hp": player_pokemon.curr_hp,
                "player_attack": player_pokemon.active_stats["attack"],
                "player_defense": player_pokemon.active_stats["defense"],
                "player_speed": player_pokemon.active_stats["speed"],
                "player_special": player_pokemon.active_stats["special"],
                "opponent_hp": opponent_pokemon.curr_hp,
                "opponent_attack": opponent_pokemon.active_stats["attack"],
                "opponent_defense": opponent_pokemon.active_stats["defense"],
                "opponent_speed": opponent_pokemon.active_stats["speed"],
                "opponent_special": opponent_pokemon.active_stats["special"],
            }]
        )

        # find all the pokemon types in the dataset of pokemons
        types = self.pokemons["types"].explode().unique()

        # add a column to the dataframe for each pokemon and for each type, with value 0 if the type is not in the pokemon's types and 1 otherwise
        for pokemon_type in types:
            X_pokemon[f"player_{pokemon_type}"] = 1 if pokemon_type in player_pokemon.types else 0
            X_pokemon[f"opponent_{pokemon_type}"] = 1 if pokemon_type in opponent_pokemon.types else 0

        # sort the dataframe such that it has the columns in the same order used to train the model
        

        return X_pokemon

    def recommendation_system(self, opponent_pokemon):
        """
        Uses the recommender to predict the probability of winning against the opponent pokemon of each pokemon (with hps > 0) in the trainer's list and suggests to the pokemon trainer which pokemon to choose.
        If no trainer's pokemon has a winning probability > 0.5, then the system suggests to the pokemon trainer to run away.
        For sure the trainer's list of pokemon contains at least one pokemon with hps > 0, since thsi function is called at the beginning of a battle.
        By game construction, indeed, when all the pokemons of the trainer are defeated, the pokemon trainer is sent to the pokemon center.

        Parameters:
        - opponent_pokemon: PokemonCharacter object representing the opponent pokemon to be faced in the battle by the pokemon trainer.

        Returns:
        - suggested_pokemon:
        """

        # iterate through the pokemons in the trainer's list to find the one with largest winning probability
        suggestion = {"name": "", "prob": 0}
        for pokemon in self.pokemon_trainer.pokemon_list:
            if pokemon.curr_hp > 0:
                X_pokemon = self.get_features(pokemon, opponent_pokemon)
                predicted_prob = self.recommender.predict_proba(X_pokemon)
                print(predicted_prob)
                
                

    def battle(self, opponent_pokemon):
        """
        Runs a battle against an opponent pokemon.

        Parameters:
        - opponent_pokemon: PokemonCharacter object representing the opponent pokemon in the battle.

        Returns:
        - boolean indicating whether the battle has been won by the trainer (True) or not (False).
          It returns False also in case the wild pokemon has been captured.
        """

        # recommend the best pokemon to choose for the battle to the user
        self.recommendation_system(opponent_pokemon)

        # options among which the pokemon trainer has to choose during an iteration of the battle
        options = ["Attack", "Change Pokemon", "Use Item", "Run Away"]

        # print some information
        type_text(f"\nThe battle against {opponent_pokemon.name.capitalize()} begins!\n")

        # the battle goes on until the opponent is catched or the opponent is defeated or the trainer runs away or all the trainer's pokemon are defeated.
        round = 1
        while True:

            # print the round number and the health points of the two pokemon involved in the battle
            type_text(f"\nRound {round}\n")
            type_text(f"\n{self.pokemon_trainer.active_pokemon.name.capitalize()}:\nHPs: {self.pokemon_trainer.active_pokemon.curr_hp}\nLevel: {self.pokemon_trainer.active_pokemon.level}\n")
            type_text(f"\n{opponent_pokemon.name.capitalize()}:\nHPs: {opponent_pokemon.curr_hp}\nLevel: {opponent_pokemon.level}\n")

            # make the pokemon trainer choose what to do in this iteration
            type_text(f"\nIt's the turn of {self.pokemon_trainer.active_pokemon.name.capitalize()}.\n")
            choice_id = choose_option(options)

            # the pokemon trainer decides to attack
            if choice_id == 0:
                if self.attack(opponent_pokemon):
                    return True                                     # the battle ends, because the opponent pokemon is defeated

            # the pokemon trainer wants to change the active pokemon
            elif choice_id == 1:
                if not self.change_pokemon():
                    continue                                        # the change cannot be done, because the active pokemon is the only pokemon left, so the user must choose another option
            
            # the pokemon trainer wants to use an item
            elif choice_id == 2:

                # there are no items in the trainer's dictionary
                if not self.pokemon_trainer.items:
                    type_text("\nYou do not have any item in your backpack. Choose another option.\n")
                    continue                                        # the user needs to select another action, because it is not possible to use items

                # make the user choose an item and use it
                if self.use_item(opponent_pokemon):
                    return False                                    # the battle ends, because the opponent pokemon has been catched
            
            # the pokemon trainer wants to run away
            elif choice_id == 3:
                if self.run_away(opponent_pokemon):
                    return False                                    # the battle ends, becasue the pokemon trainer has run away

            # make the opponent pokemon attack the trainer's active pokemon with a move sampled uniformly at random among the available ones
            if self.opponent_pokemon_turn(opponent_pokemon):
                
                # the pokemon trainer goes to the pokemon center since all trainer's pokemon are K.O.
                self.pokemon_center_action()
                return False                                        # the battle ends, because the trainer's pokemon are K.O.

            # check whether all trainer's pokemon as well as the wild pokemon have all moves with pps that are finished
            if self.check_pps(opponent_pokemon):
                print("..")
                return False                                        # the battle ends, because all trainer's pokemon and the wild pokemon have no more pps

            # update the round number
            round += 1

    def explore_action(self, p=0.8):
        """
        Makes the pokemon trainer explore the world, with a given probability of finding a wild pokemon opponent.

        Parameters:
        - p: float representing the probability of finfing a wild pokemon.
        """

        # print some information
        clear_terminal()
        type_text("Exploring the Pokemon World")
        type_text(" ...", delay=0.5)
        type_text("\n\n")

        # a wild pokemon has been encountered
        if random.random() <= 0.8:
            
            # sample uniformly at random a wild pokemon among the loaded ones
            sampled_pokemon = self.to_pokemon_character(self.pokemons.sample().iloc[0])

            # assign a random level from 1 to 20 to the wild pokemon
            sampled_pokemon.set_level(random.randint(1, 20))

            # print some information
            type_text(f"A wild {sampled_pokemon.name.capitalize()} appears!\n")

            # start a battle against the sampled wild pokemon
            level_up = self.battle(sampled_pokemon)

            # increment the level of the active pokemon by 1 in case the wild pokemon was defeated and the active pokemon does not have the maximum level allowed
            if level_up:
                if self.pokemon_trainer.active_pokemon.level < self.max_level_game:
                    self.pokemon_trainer.active_pokemon.set_level(self.pokemon_trainer.active_pokemon.level + 1)
                    type_text(f"{self.pokemon_trainer.name}'s {self.pokemon_trainer.active_pokemon.name.capitalize()} increases its level!\n")
                    type_text(f"The new level of {self.pokemon_trainer.active_pokemon.name.capitalize()} is {self.pokemon_trainer.active_pokemon.level}.\n")
                else:
                    type_text(f"{self.pokemon_trainer.active_pokemon.name.capitalize()} already has the maximum level allowed in the game ({self.max_level_game}).\n")
        
        # no wild pokemon has been encounterd
        else:
            type_text("There is no wild pokemon around.\n")

    def pokemon_center_action(self):
        """
        Makes the pokemon trainer go to the pokemon center, restoring the HPs of every pokemon in the trainer's list and the PPs of all the moves of all pokemon.
        """
        
        # print some information
        clear_terminal()
        type_text("Welcome to the Pokemon Center!\n\nWe are restoring the HPs and PPs of all your pokemons")
        type_text(" ...", delay=0.5)
        type_text("\n")

        # restore the hp of every pokemon in the pokemon trainer's list
        for pokemon in self.pokemon_trainer.pokemon_list:
            pokemon.curr_hp = pokemon.active_stats["hp"]
        
        # restore the pp of every move of each pokemon
        for pokemon in self.pokemon_trainer.pokemon_list:
            for move in pokemon.moves:
                move_name = move["name"]
                pokemon.curr_pps[move_name] = move["pp"]

        # print some information
        type_text("\nAll your pokemon are restored.\nHope not to see you soon!\n")

    def pokemon_store_action(self):
        """
        Makes the pokemon trainer go to the pokemon store to fill all the trainer's items to their maximum: 10 potions and 10 pokeballs.
        """

        # items present in the store
        store_items = ["potion", "pokeball"]

        # print some information
        clear_terminal()
        type_text("Hello, happy to see you at the Pokemon Store.\n\nHere we go with the items you ordered")
        type_text(" ...", delay=0.5)
        type_text("\n\n")

        # check the current quantities for the items present in the store that the trainer has
        curr_items_quantities = {}
        for item in store_items:
            curr_items_quantities[item] = self.pokemon_trainer.items.get(item, 0)    # set the value to 0 if the item is not in pokemon_trainer.items

        # fill the pokemon trainer's items
        for item in store_items:
            quantity_to_sell = 10 - curr_items_quantities[item]
            self.pokemon_trainer.add_items(item, quantity_to_sell)

        # print some information
        type_text("\nThank you for purchasing! See you soon!\n")

    def exit_action(self):
        """
        Exits the game and saves current data if requested by the user.
        """

        # save data if the user wants
        choice = choose_option(["Yes", "No"], "Do you want to save data?")
        if choice == 0:
            os.makedirs(self.savings_folder, exist_ok=True)
            saving_name = ""
            while True:
                clear_terminal()
                type_text(f"How do you want to name the saving?\n")
                saving_name = input("> ")
                if saving_name + ".pickle" in os.listdir(self.savings_folder):
                    overwrite = choose_option(["Yes", "No"], f"A previous saving with name \"{saving_name}\" exists. Do you want to overwrite it?")
                    if overwrite == 1:
                        continue
                type_text("Saving data...\n")
                with open(os.path.join(self.savings_folder, saving_name + ".pickle"), "wb") as file:
                    pickle.dump(self.pokemon_trainer, file)
                type_text("Your data has been successfully saved!\n\nSee you soon!\n\n")
                break
        
        # do not save and just exit the game
        else:
            type_text("All right!\n\nSee you soon!\n\n")

    def run(self):
        """
        Runs the game.
        """

        # actions among which the player can choose
        actions = ["Explore", "Go to the Pokemon Center", "Go to the Pokemon Store", "Quit"]

        # make the player play until the player decides to quit
        while True:

            # make the player choose the next action
            chosen_id = choose_option(actions)

            # run the action selected by the user
            if chosen_id == 0:
                self.explore_action()
            elif chosen_id == 1:
                self.pokemon_center_action()
            elif chosen_id == 2:
                self.pokemon_store_action()
            elif chosen_id == 3:
                self.exit_action()
                break
