from genericpath import exists
import logging
import os
from typing import Optional, Dict, Any
import pathlib

from jinja2 import Environment, FileSystemLoader, select_autoescape


def get_templates_dir():
    # use the `templates` dir that is a sibling to this file
    path = os.path.abspath(__file__)
    path = os.path.dirname(path)
    return os.path.join(path, 'templates')


class TemplateTreeJob(object):
    """
    Reproduces a templated file tree into a target directory, making
    necessary substitutions.
    """

    VALID_EXISTS_POLICIES = [
        "skip",
        "error",
        "overwrite",
    ]

    def __init__(
        self,
        template_root: str,
        target_root: str,
        template_context: Dict[str, Any] = {},
        filename_substitutions: Dict[str, str] = {},
        exists_policy: str = "error"
    ):
        self.template_root = template_root
        self.target_root = target_root
        self.template_context = template_context

        if exists_policy not in self.VALID_EXISTS_POLICIES:
            valid_policies_str = ", ".join(self.VALID_EXISTS_POLICIES)
            raise ValueError(
                f"exists_policy must be one of: {valid_policies_str}")
        self.exists_policy = exists_policy

        self.filename_substitutions = filename_substitutions

    def run(self):
        logging.info(
            f"Rendering template: {self.template_root}->{self.target_root}")

        loader = FileSystemLoader(self.template_root)
        env = Environment(loader=loader,
                          autoescape=select_autoescape(),
                          keep_trailing_newline=True)

        # apply templates in each directory
        for dir_name, _, file_list in os.walk(self.template_root):

            relative_dir = dir_name[len(self.template_root) + 1:]
            target_dir = self._substitute_name(relative_dir)
            target_dir = os.path.join(self.target_root, target_dir)
            self._ensure_dir(target_dir)

            for file_name in file_list:
                file_load_path = os.path.join(relative_dir, file_name)
                file_write_path = os.path.join(target_dir, file_name)
                file_write_path = self._substitute_name(file_write_path)

                # handle files that already exist according to policy
                if os.path.exists(file_write_path):
                    message = ""
                    if(self.exists_policy == "skip"):
                        logging.info(
                            f"{file_write_path} - SKIPPED")
                    elif(self.exists_policy == "error"):
                        raise IOError(
                            f"File '{file_write_path}' already exists.")
                    elif(self.exists_policy == "overwrite"):
                        template = env.get_template(file_load_path)
                        with open(file_write_path, 'w') as f:
                            f.write(template.render(**self.template_context))
                        logging.info(
                            f"{file_write_path} - OVERWRITTEN")
                    else:
                        raise ValueError(
                            f"Encountered unimplemented exists_policy: {self.exists_policy}")

                # if file does not exist, render from template
                else:
                    template = env.get_template(file_load_path)
                    with open(file_write_path, 'w') as f:
                        f.write(template.render(**self.template_context))
                    logging.info(f"{file_write_path} - CREATED")

    def _ensure_dir(self, directory: str):
        if not os.path.exists(directory):
            os.makedirs(directory)
            logging.info(f"{directory} - CREATED")
        elif not os.path.isdir(directory):
            raise IOError(f"Path is a non-directory file: '{directory}'")
        else:
            logging.info(f"{directory} - EXISTS")

    def _substitute_name(self, path: str):
        for key in self.filename_substitutions:
            value = self.filename_substitutions[key]
            path = path.replace(key, value)
        return path
