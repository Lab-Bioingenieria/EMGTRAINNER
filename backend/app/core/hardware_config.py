import os
import json
from typing import Dict, Any

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "hardware_config.json")

class HardwareConfigManager:
    _instance = None

    def __init__(self):
        self.main_port = None
        self.independent_data_acquisition = False
        self.data_port = None
        self.load_config()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_config(self):
        """Loads configuration from JSON file or environment variables."""
        if os.path.exists(CONFIG_FILE_PATH):
            try:
                with open(CONFIG_FILE_PATH, "r") as f:
                    data = json.load(f)
                    self.main_port = data.get("main_port")
                    self.independent_data_acquisition = data.get("independent_data_acquisition", False)
                    self.data_port = data.get("data_port")
            except Exception as e:
                print(f"Failed to load hardware config from {CONFIG_FILE_PATH}: {e}")
                self._load_defaults()
        else:
            self._load_defaults()

    def _load_defaults(self):
        # Fallback to env vars if file not found
        self.main_port = os.getenv("DYNAMIXEL_PORT")
        self.independent_data_acquisition = False
        self.data_port = None

    def save_config(self, main_port: str = None, independent_data_acquisition: bool = False, data_port: str = None):
        """Saves configuration to JSON file and updates in memory."""
        self.main_port = main_port
        self.independent_data_acquisition = independent_data_acquisition
        self.data_port = data_port
        
        data = {
            "main_port": self.main_port,
            "independent_data_acquisition": self.independent_data_acquisition,
            "data_port": self.data_port
        }
        
        try:
            with open(CONFIG_FILE_PATH, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Failed to save hardware config to {CONFIG_FILE_PATH}: {e}")

    def get_config(self) -> Dict[str, Any]:
        return {
            "main_port": self.main_port,
            "independent_data_acquisition": self.independent_data_acquisition,
            "data_port": self.data_port
        }

hardware_config = HardwareConfigManager.get_instance()
