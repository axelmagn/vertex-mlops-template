"""
Contains configuration management logic, most importantly the 'Config' class
and 'get_config' function.

This module also manages a global configuration object, which may be initialized
with 'init_global_config' and retrieved with 'get_config'.

"""
from typing import Any, List, Dict, Optional

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
                 config_file_paths: Optional[List[str]] = None,
                 config_strings: Optional[List[str]] = None,
                 ):
        """Config constructor.

        Args:
            config_init:        Initial configuration dictionary.
            config_file_paths:  Paths to configuration files to be loaded in
                                order.
            config_strings:     yaml strings containing dictionaries to add.
        """
        config_init = config_init if config_init is not None else {}
        config_file_paths = config_file_paths if config_file_paths is not None else []
        config_strings = config_strings if config_strings is not None else []

        self._config = config_init
        self.config_file_paths = config_file_paths
        for path in config_file_paths:
            self.load_config(path)

        for config_str in config_strings:
            self.loads(config_str)

    def load_config(self, config_path: str):
        """Load a config file.

        Conflicting top-level keys in the existing config are overwritten with
        the contents of the new config.

        Args:
            config_path: path of the config file to load.
        """
        with open(config_path, 'r') as file:
            _config = yaml.safe_load(file)
        self._config.update(_config)

    def dumps(self, stream=None):
        """Dump config to string or stream"""
        return yaml.safe_dump(self._config, stream=stream)

    def loads(self, stream):
        """Update config additively with supplied string or stream"""
        _config = yaml.safe_load(stream)
        self._config.update(_config)

    def get(self, key, default=None):
        """Retrieve a config value by key"""
        return self._config.get(key, default)

    def set(self, key, value):
        """Set a config value by key"""
        self._config[key] = value

    def __getitem__(self, key):
        return self._config[key]
