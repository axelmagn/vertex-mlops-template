import os
import yaml
import re
from typing import Any, Optional


class Config(object):

    FILE_MATCHER = re.compile(r"(?P<name>\w+)\.ya?ml")

    def __init__(
        self,
        config_root: str = "./config",
        config_environment: Optional[str] = None
    ):
        self.config_root = config_root
        self.config_env = config_environment
        self._configs = {}
        self.load_configs()

    def load_configs(self):
        # TODO(axelmagn): docstring
        for config_file in sorted(os.listdir(self.config_root)):
            self.load_file_if_yaml(config_file)
        if self.config_env is not None:
            config_env_root = os.path.join(self.config_root, self.config_env)
            for config_file in sorted(os.listdir(config_env_root)):
                self.load_file_if_yaml(config_file)

    def load_file_if_yaml(self, config_file):
        match = self.FILE_MATCHER.match(config_file)
        if match is not None:
            name = match.group("name")
            path = os.path.join(self.config_root, config_file)
            with open(path, 'r') as f:
                setattr(self, name, yaml.load(f))
