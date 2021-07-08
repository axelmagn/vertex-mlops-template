import yaml
from typing import Any, List, Dict

_CONFIG = None


def init_global_config(*args, **kwargs):
    """Initialize the CONFIG global as a new Config object with passed args."""
    global _CONFIG
    _CONFIG = Config(*args, **kwargs)
    return _CONFIG


def get_config():
    """Retrieve the global config"""
    global _CONFIG
    return _CONFIG


class Config(object):
    # TODO(axelmagn): docstring
    def __init__(self,
                 config_init: Dict[str, Any] = {},
                 config_file_paths: List[str] = [],
                 config_strings: List[str] = [],
                 ):
        """Config constructor.

        Args:
            config_init:        Initial configuration dictionary.
            config_file_paths:  Paths to configuration files to be loaded in 
                                order.
        """
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
        with open(config_path, 'r') as f:
            _config = yaml.safe_load(f)
        self._config.update(_config)

    def dumps(self, stream=None):
        """Dump config to string or stream"""
        return yaml.safe_dump(self._config, stream=stream)

    def loads(self, stream):
        """Update config additively with supplied string or stream"""
        _config = yaml.safe_load(stream)
        self._config.update(_config)

    def __getitem__(self, key):
        return self._config[key]
