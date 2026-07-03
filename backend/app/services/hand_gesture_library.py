from typing import Dict

GestureDefinition = Dict[str, Dict[str, float]]

GESTURES: Dict[str, Dict[str, GestureDefinition]] = {
    "REST": {
        "Six_DOF_Right": {
            "thumb": {"MCP_FE": 30, "CMC_AA": 35, "CMC_FE": 45},
            "index": {"PIP": 45, "MCP": 30},
            "middle": {"PIP": 55, "MCP": 35},
            "ring": {"PIP": 45, "MCP": 40},
            "pinky": {"PIP": 35, "MCP": 45},
        }
    },
    "SALUTE": {
        "Six_DOF_Right": {
            "thumb": {"MCP_FE": 30, "CMC_AA": 35, "CMC_FE": 45},
            "index": {"MCP": 0, "PIP": 0},
            "middle": {"MCP": 0, "PIP": 0},
            "ring": {"MCP": 0, "PIP": 0},
            "pinky": {"MCP": 0, "PIP": 0},
        }
    },
}
