from typing import Dict

GestureDefinition = Dict[str, Dict[str, float]]
# finger -> joint -> angle_deg

GESTURES: Dict[str, Dict[str, GestureDefinition]] = {
    "REST": {
        "Six_DOF_Right": {
            "thumb": {
                "MCP_FE": 30,
                "CMC_AA": 35,
                "CMC_FE": 45,
            },
            "index": {
                "PIP": 45,
                "CMP": 30,
            },
            "middle": {
                "PIP": 55,
                "MCP": 35,
            },
            "ring": {
                "PIP": 45,
                "MCP": 40,
            },
            "pinky": {
                "PIP": 35,
                "MCP": 45,
            },
        },

        "Two_DOF_Left": {
            "thumb": {
                "MCP_FE": 20,
            },
            "phalanx": {
                "II_MCP_FE": 30,
                "II_PIP_FE": 45,
                "III_MCP_FE": 30,
                "III_PIP_FE": 45,
                "IV_MCP_FE": 30,
                "IV_PIP_FE": 45,
                "V_MCP_FE": 30,
                "V_PIP_FE": 45,
            },
        },
    },

    "SALUTE": {
        "Six_DOF_Right": {
            "thumb": {
                "MCP_FE": 30,
                "CMC_AA": 20,
                "CMC_FE": 40,
            },
            "index":  {"MCP": 5, "PIP": 10},
            "middle": {"MCP": 5, "PIP": 10},
            "ring":   {"MCP": 5, "PIP": 10},
            "pinky":  {"MCP": 5, "PIP": 10},
        },
        
        "Two_DOF_Left": {
            "thumb": {
                "MCP_FE": 0,
            },
            "phalanx": {
                "II_MCP_FE": 0,
                "II_PIP_FE": 10,
                "III_MCP_FE": 0,
                "III_PIP_FE": 10,
                "IV_MCP_FE": 0,
                "IV_PIP_FE": 10,
                "V_MCP_FE": 0,
                "V_PIP_FE": 10,
            },
        },
    },


    "POINT": {
        "Six_DOF_Right": {
            "thumb": {
                "MCP_FE": 65,
                "CMC_AA": 40,
                "CMC_FE": 45,
            },
            "index": {
                "PIP": 0,
                "CMP": 0,
            },
            "middle": {
                "PIP": 100,
                "MCP": 75,
            },
            "ring": {
                "PIP": 100,
                "MCP": 75,
            },
            "pinky": {
                "PIP": 100,
                "MCP": 75,
            },
        },
    },

    "LIKE": {
        "Six_DOF_Right": {
            "thumb": {
                "MCP_FE": 65,
                "CMC_AA": 40,
                "CMC_FE": 45,
            },
            "index": {
                "PIP": 0,
                "CMP": 0,
            },
            "middle": {
                "PIP": 100,
                "MCP": 75,
            },
            "ring": {
                "PIP": 100,
                "MCP": 75,
            },
            "pinky": {
                "PIP": 100,
                "MCP": 75,
            },
        },
    },

    "OPEN": {
        "Six_DOF_Right": {
            "thumb": {
                "MCP_FE": 10,
                "CMC_AA": 0,
                "CMC_FE": 30,
            },
            "index":  {"PIP": 0, "MCP": 0},
            "middle": {"PIP": 0, "MCP": 0},
            "ring":   {"PIP": 0, "MCP": 0},
            "pinky":  {"PIP": 0, "MCP": 0},
        },
        
        "Two_DOF_Left": {
            "thumb": {
                "MCP_FE": 0,
            },
            "phalanx": {
                "II_PIP_FE":  0,  "II_MCP_FE": 0,
                "III_PIP_FE": 0, "III_MCP_FE": 0,
                "IV_PIP_FE":  0,  "IV_MCP_FE": 0,
                "V_PIP_FE":   0,   "V_MCP_FE": 0,
            },
        },
    },

    "CLOSE": {
        "Six_DOF_Right": {
            "thumb": {
                "MCP_FE": 10,
                "CMC_AA": 0,
                "CMC_FE": 30,
            },
            "index":  {"PIP": 90, "MCP": 90},
            "middle": {"PIP": 90, "MCP": 90},
            "ring":   {"PIP": 90, "MCP": 90},
            "pinky":  {"PIP": 90, "MCP": 90},
        },
        
        "Two_DOF_Left": {
            "thumb": {
                "MCP_FE": 0,
            },
            "phalanx": {
                "II_PIP_FE":  0,  "II_MCP_FE": 0,
                "III_PIP_FE": 0, "III_MCP_FE": 0,
                "IV_PIP_FE":  0,  "IV_MCP_FE": 0,
                "V_PIP_FE":   0,   "V_MCP_FE": 0,
            },
        },
    },
}
