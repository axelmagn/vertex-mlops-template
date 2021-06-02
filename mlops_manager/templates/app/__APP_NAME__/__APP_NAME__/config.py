import yaml
import sys
from typing import Any, List


def init_global_config(*args, **kwargs):
    """Initialize the CONFIG global as a new Config object with passed args."""
    global CONFIG
    CONFIG = Config(*args, **kwargs)


class Config(object):
    # TODO(axelmagn): docstring
    def __init__(self, config_file_paths: List[str] = []):
        """Config constructor.

        Args:
            config_file_paths:  Paths to configuration files to be loaded in 
                                order.
        """
        self._config = {}
        for path in config_file_paths:
            self.load_config(path)

    def load_config(self, config_path: str):
        """Load a config file.

        Conflicting top-level keys in the existing config are overwritten with
        the contents of the new config.  

        Args:
            config_path: path of the config file to load.
        """
        with open(config_path, 'r') as f:
            _config = yaml.safe_load(f)
        self._config.update(_config)

    def __getitem__(self, key):
        return self._config[key]
