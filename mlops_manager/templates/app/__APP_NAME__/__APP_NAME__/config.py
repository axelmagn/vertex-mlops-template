import os
import yaml
import re
from typing import Any, Optional

DEFAULT_CONFIG_ROOT = os.path.dirname(os.path.realpath(__file__))


class Config(object):
    # TODO(axelmagn): docstring

    FILE_MATCHER = re.compile(r"(?P<name>\w+)\.ya?ml$")

    def __init__(
        self,
        config_root: str = DEFAULT_CONFIG_ROOT,
        config_environment: Optional[str] = None
    ):
        # TODO(axelmagn): docstring
        self.config_root = config_root
        self.config_env = config_environment
        self._configs = {}
        self.load_configs()

    def load_configs(self):
        # TODO(axelmagn): docstring
        for config_file in sorted(os.listdir(self.config_root)):
            self.load_file_if_yaml(config_file)
        if self.config_env is not None:
            config_env_root = os.path.join(
                self.config_root, "environments", self.config_env)
            for config_file in sorted(os.listdir(config_env_root)):
                self.load_file_if_yaml(config_file)

    def load_file_if_yaml(self, config_file: str):
        # TODO(axelmagn): docstring
        match = self.FILE_MATCHER.match(config_file)
        if match is not None:
            name = match.group("name")
            path = os.path.join(self.config_root, config_file)
            with open(path, 'r') as f:
                setattr(self, name, yaml.safe_load(f))
