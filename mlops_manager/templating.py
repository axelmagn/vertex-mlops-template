from genericpath import exists
import logging
import os
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

NAME_SUBSTITUTION_MARKER = "__NAME__"


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

    def __init__(self, template_root: str, target_root: str, template_context={}, exists_policy: str = "error", sub_name: Optional[str] = None):
        self.template_root = template_root
        self.target_root = target_root
        self.template_context = template_context

        if exists_policy not in self.VALID_EXISTS_POLICIES:
            valid_policies_str = ", ".join(self.VALID_EXISTS_POLICIES)
            raise ValueError(
                f"exists_policy must be one of: {valid_policies_str}")
        self.exists_policy = exists_policy

        self.sub_name = sub_name

    def run(self):
        loader = FileSystemLoader(self.template_root)
        env = Environment(loader=loader,
                          autoescape=select_autoescape())

        # apply templates in each directory
        for dir_name, _, file_list in os.walk(self.template_root):

            relative_dir = dir_name[len(self.template_root):]
            target_dir = os.path.join(self.target_root, relative_dir)
            if self.sub_name is not None:
                target_dir = self._substitute_name(target_dir)
            self._ensure_dir(target_dir)

            for file_name in file_list:
                file_load_path = os.path.join(relative_dir, file_name)
                file_write_path = os.path.join(target_dir, file_name)

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
        # recursively split up the path and perform substitution
        def split_sub_all(path):
            if not path:
                return tuple()
            (head, tail) = os.path.split(path)
            if tail == NAME_SUBSTITUTION_MARKER:
                tail = self.sub_name
            return split_sub_all(head) + (tail,)
        return os.path.join(*split_sub_all(path))
