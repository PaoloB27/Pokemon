import random
from pokemon_trainer import PokemonTrainer
from pokemon_character import PokemonCharacter
from utils import clear_terminal, type_text, choose_option

class SimpleGame:

    def __init__(self, starter_pokemons, moves):
        """
        Creates a simple game that consists of a single battle between the starter pokemon chosen by the user and another starter pokemon sampled uniformly at random.

        Parameters:
        - starter_pokemons: list of starter pokemons, represented as dictionaries.
        - moves: list of pokemon moves, represented as dictionaries.
        """
        
        # set the pokemon moves
        self.moves = moves

        # initialize the poemon trainer with information provided by the user
        self.pokemon_trainer = self.initialize_pokemon_trainer(starter_pokemons)

        # sample uniformly at random a starter pokemon to be faced in the battle
        self.opponent_pokemon = self.pokemon_from_dict(random.choice(starter_pokemons))

    def pokemon_from_dict(self, pokemon_info):
        """
        Initializes a PokemonCharacter object from an input dictionary.

        Parameters:
        - pokemon_info: dictionary that must have the following entries:
                        - name: string with the name of the pokemon;
                        - base_stast: dictionary with the basic statistics of the pokemon;
                        - moves: list of strings with the names of the moves of the pokemon;
                        - national_pokedex_number: integer resperenting the national pokedex number of the pokemon;
                        - types: list of strings with the types of the pokemon.
        
        Returns:
        - pokemon: PokemonCharacter initialized with the input information.
        """

        # initialize a PokemonCharacter with the input information
        moves_dict = {move["name"]: move for move in self.moves}
        pokemon = PokemonCharacter(
            name=pokemon_info["name"],
            national_pokedex_number=pokemon_info["national_pokedex_number"],
            types=pokemon_info["types"],
            base_stats=pokemon_info["base_stats"],
            moves=[moves_dict[m] for m in pokemon_info["moves"]]
        )

        return pokemon

    def initialize_pokemon_trainer(self, starter_pokemons):
        """
        Initializes a PokemonTrainer with a name chosen by the user and a starter pokemon chosen by the user among the input ones.

        Parameters:
        - starter_pokemons: list of starter pokemons, represented as dictionaries.

        Returns:
        - trainer: PokemonTrainer object representing the initialized pokemon trainer.
        """

        # ask the user (i.e., the pokemon trainer) to enter his name
        type_text("\nHello pokemon trainer! What is your name?\n")
        trainer_name = input("> ")
        clear_terminal()
        
        # create the pokemon trainer
        trainer = PokemonTrainer(trainer_name)

        # make the user choose the starter pokemon
        starter_pokemon_choice = choose_option([pokemon["name"] for pokemon in starter_pokemons], f"Ok {trainer_name}, I want you to choose one of the following pokemons:")
        clear_terminal()

        # create the starter pokemon and add it to the pokemon trainer's list
        chosen_pokemon = starter_pokemons[int(starter_pokemon_choice)]
        chosen_pokemon = self.pokemon_from_dict(chosen_pokemon)
        type_text(f"You chose {chosen_pokemon.name.capitalize()}! Great choice {trainer_name}!\n\n")
        trainer.pokemon_list.append(chosen_pokemon)

        return trainer

    def trainer_pokemon_attack(self):
        """
        The trainer's pokemon attacks the opponent pokemon.

        Returns:
        - is_defeated: boolean indicating whether the opponent pokemon is defeated or not.
        """

        # if the pokemon does not have any move with pps > 0, then return
        if not [pp for pp in self.pokemon_trainer.pokemon_list[0].curr_pps.values() if pp > 0]:
            type_text(f"\nOh no! {self.pokemon_trainer.pokemon_list[0].name.capitalize()} finished all the PPs!\n")
            return False

        # make the pokemon trainer choose a move among those that still have some pps
        possible_moves = [move_name for move_name, pp in self.pokemon_trainer.pokemon_list[0].curr_pps.items() if pp > 0]
        options = [f"{move_name.capitalize()} | {pp} PP" for move_name, pp in self.pokemon_trainer.pokemon_list[0].curr_pps.items() if pp > 0]
        chosen_move = possible_moves[choose_option(options, question_sentence=f"Which move do you want {self.pokemon_trainer.pokemon_list[0].name.capitalize()} to use?")]

        # make the pokemon attack the opponent pokemon with the chosen move
        self.pokemon_trainer.pokemon_list[0].use_move(chosen_move, self.opponent_pokemon)

        # check whether the opponent pokemon is defeated
        if self.opponent_pokemon.curr_hp <= 0:
            type_text(f"\nCongratulations! {self.opponent_pokemon.name.capitalize()} is defeated!\n")
            return True
        
        # the opponent pokemon is not defeated
        return False

    def opponent_pokemon_attack(self):
        """
        Makes the opponent pokemon attack the trainer's pokemon.

        Returns:
        - is_defeated: boolean indicating whether the trainer's pokemon has been defeated or not.
        """

        # print some information    
        type_text(f"\nIt's the turn of {self.opponent_pokemon.name.capitalize()}.\n\n")

        # if the wild pokemon does not have any move with pp > 0, then return
        if not [pp for pp in self.opponent_pokemon.curr_pps.values() if pp > 0]:
            type_text(f"\nOh no! {self.opponent_pokemon.name.capitalize()} finished all the PPs!\n")
            return False

        # make the opponent pokemon attack the trainer's pokemon with a move sampled uniformly at random among the available ones
        self.opponent_pokemon.use_move(random.choice([move_name for move_name, pp in self.opponent_pokemon.curr_pps.items() if pp > 0]), self.pokemon_trainer.pokemon_list[0])
        
        # check whether the trainer's pokemon is defeated
        if self.pokemon_trainer.pokemon_list[0].curr_hp <= 0:
            type_text(f"\n{self.pokemon_trainer.pokemon_list[0].name.capitalize()} is defeated!\n")
            return True

        # the trainer's pokemon is not defeated
        return False

    def check_pps(self):
        """
        Checks whether both the trainer's poemon and the sampled pokemon do not have any move with pp > 0.

        Returns:
        - no_pps: boolean indicating whether both the trainer's poemon and the sampled pokemon do not have any move with pp > 0.
        """

        # check whether at least a move of any of the two pokemons has at least 1 pp
        for pokemon in [self.pokemon_trainer.pokemon_list[0], self.opponent_pokemon]:
            for pp in pokemon.curr_pps.values():
                if pp > 0:
                    return False
                
        # no pokemon has at least one move with pp > 0, so tell the user that the battle ends
        type_text(f"\n{self.pokemon_trainer.pokemon_list[0].name.capitalize()} has no move with pp > 0!\n")
        type_text(f"Even {self.opponent_pokemon.name.capitalize()} has no move with pp > 0!\n")
        type_text(f"The battle ends.\n")
        return True

    def battle(self):
        """
        Runs a battle between the starter pokemon chosen by the pokemon trainer and the sampled opponent starter pokemon.
        """

        # print some information
        type_text(f"The battle against {self.opponent_pokemon.name.capitalize()} begins!\n")

        # the battle goes on until one of the two pokemons is defeated
        round = 1
        while True:

            # print the round number and the health points of the two pokemon involved in the battle
            type_text(f"\nRound {round}\n")
            type_text(f"\n{self.pokemon_trainer.pokemon_list[0].name.capitalize()} HP: {self.pokemon_trainer.pokemon_list[0].curr_hp}\n")
            type_text(f"{self.opponent_pokemon.name.capitalize()} HP: {self.opponent_pokemon.curr_hp}\n")

            # make the pokemon trainer choose what to do in this iteration
            type_text(f"\nIt's the turn of {self.pokemon_trainer.pokemon_list[0].name.capitalize()}.\n")

            # the trainer's pokemon attacks
            if self.trainer_pokemon_attack():
                return                                      # the battle ends, because the opponent pokemon is defeated

            # the opponent pokemon attacks
            if self.opponent_pokemon_attack():
                return                                      # the battle ends, because the trainer's pokemon are K.O.

            # check whether none of the two pokemons involved in the battle has at least one move with at least 1 pp
            if self.check_pps():
                return                                      # the battle ends, because both pokemons have no more pps

            # update the round number
            round += 1
