
# moves
moves = [
    {
        "name": "tackle",
        "type": "normal",
        "category": "physical",
        "power": 35,
        "accuracy": 0.95,
        "pp": 35
    },

    {
        "name": "razor leaf",
        "type": "grass",
        "category": "physical",
        "power": 55,
        "accuracy": 0.95,
        "pp": 25
    },

    {
        "name": "ember",
        "type": "fire",
        "category": "special",
        "power": 40,
        "accuracy": 1.0,
        "pp": 25
    },

    {
        "name": "water gun",
        "type": "water",
        "category": "special",
        "power": 40,
        "accuracy": 1.0,
        "pp": 25
    }
]

# starter pokemon
starter_pokemon = [
    {
        "national_pokedex_number": 1,
        "name": "Bulbasaur",
        "types": ["grass", "poison"],
        "base_stats": {
            "hp": 45,
            "attack": 49,
            "defense": 49,
            "speed": 45,
            "special": 65
        },
        "moves": ["tackle", "razor leaf"]
    },

    {
        "national_pokedex_number": 4,
        "name": "Charmander",
        "types": ["fire"],
        "base_stats": {
            "hp": 39,
            "attack": 52,
            "defense": 43,
            "speed": 65,
            "special": 50
        },
        "moves": ["tackle", "ember"]
    },

    {
        "national_pokedex_number": 7,
        "name": "Squirtle",
        "types": ["water"],
        "base_stats": {
            "hp": 44,
            "attack": 48,
            "defense": 65,
            "speed": 43,
            "special": 50
        },
        "moves": ["tackle", "water gun"]
    }
]