"""
Contains configuration management logic, most importantly the 'Config' class
and 'get_config' function.

This module also manages a global configuration object, which may be initialized
with 'init_global_config' and retrieved with 'get_config'.

"""
from typing import Any, Dict, Optional

import yaml

_CONFIG = None


def init_global_config(*args, **kwargs):
    """Initialize the CONFIG global as a new Config object with passed args."""
    global _CONFIG  # pylint: disable=global-statement
    _CONFIG = Config(*args, **kwargs)
    return _CONFIG


def get_config():
    """Retrieve the global config"""
    global _CONFIG  # pylint: disable=global-statement
    return _CONFIG


class Config:
    """Configuration object managing a dictionary tree of keys and values."""

    def __init__(self,
                 config_init: Optional[Dict[str, Any]] = None,
                 config_file_path: Optional[str] = None,
                 config_string: Optional[str] = None,):
        """Config constructor.

        Args:
            config_init:        Initial configuration dictionary.
            config_file_paths:  Paths to configuration files to be loaded in
                                order.
            config_strings:     yaml strings containing dictionaries to add.
        """
        self._config = {}
        if config_init is not None:
            self._config = config_init
        elif config_string is not None:
            self.loads(config_string)
        elif config_file_path is not None:
            self.load_config_file(config_file_path)

    def load_config_file(self, config_path: str):
        """Load a config file.

        Conflicting top-level keys in the existing config are overwritten with
        the contents of the new config.

        Args:
            config_path: path of the config file to load.
        """
        with open(config_path, 'r') as file:
            self._config = yaml.safe_load(file)

    def dumps(self, stream=None):
        """Dump config to string or stream"""
        return yaml.safe_dump(self._config, stream=stream)

    def loads(self, stream):
        """Update config additively with supplied string or stream"""
        self._config = yaml.safe_load(stream)

    def get(self, key, default=None):
        """Retrieve a config value by key"""
        return self._config.get(key, default)

    def set(self, key, value):
        """Set a config value by key"""
        self._config[key] = value

    def __getitem__(self, key):
        return self._config[key]
