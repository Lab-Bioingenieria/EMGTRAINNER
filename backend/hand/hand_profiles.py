# hand/hand_profiles.py

HAND_PROFILES = {
    "PROTESIS_2GDL": {
        "motors": [1, 3, 4],
        "velocity": 40,
        "current": 200,
        "gestures": {
            "OPEN_HAND": {1: 2048, 3: 2048, 4: 2048},
            "CLOSE_HAND": {1: 3000, 3: 3000, 4: 3000},
            "PINCH": {1: 2800, 3: 2900, 4: 2200}
        }
    },

    "PROTESIS_6GDL": {
        "motors": list(range(1, 11)),
        "velocity": 80,
        "current": 300,
        "gestures": {
            "OPEN_HAND": {i: 2048 for i in range(1, 11)},
            "POWER_GRASP": {
                1: 3200, 2: 2600,
                3: 3100, 4: 3000,
                5: 3100, 6: 3000,
                7: 3100, 8: 3000,
                9: 3100, 10: 3000
            }
        }
    }
}
