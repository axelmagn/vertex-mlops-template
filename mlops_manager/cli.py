from .templating import get_templates_dir
from argparse import ArgumentParser
import os
import yaml

_PARSER = ArgumentParser()
_PARSER.add_argument("--log_level", help="Specify log level", type=str,
                     choices=["debug", "info", "warning", "error", "critical"],
                     default="info")
_COMMANDS_PARSER = _PARSER.add_subparsers(title="commands", dest="command")


def command(args=[], parent=_COMMANDS_PARSER, strict=True):
    """
    Decorator for CLI commands.

    see commands.py for examples.
    """
    def decorator(func):
        func.strict = strict
        parser = parent.add_parser(func.__name__, description=func.__doc__)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)
    return decorator


def template_command(args=[], parent=_COMMANDS_PARSER, strict=True):
    """
    Decorator for a function that handles a subcommand for each template
    """

    def decorator(func):
        func.strict = strict

        name = func.__name__
        if name.endswith("_template"):
            name = name[:-len("_template")]
        parser = parent.add_parser(name, description=func.__doc__)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)
        templates_subparser = parser.add_subparsers(
            title="templates", dest="template")

        with os.scandir(get_templates_dir()) as scan:
            for entry in scan:
                # load each template directory as a subcommand
                if entry.is_dir():
                    template_parser = templates_subparser.add_parser(
                        entry.name)

                    with os.scandir(entry.path) as scan:
                        variants = [
                            variant.name for variant in scan
                            if variant.is_dir()
                        ]

                    if "examples" in variants:
                        variants.remove("examples")
                        examples_path = os.path.join(entry.path, "examples")
                        with os.scandir(examples_path) as scan:
                            examples = [
                                example.name for example in scan
                                if example.is_dir()
                            ]
                        template_parser.add_argument(
                            "--example",
                            help="example to included",
                            action='append',
                            choices=examples,
                            dest='examples',
                            default=[])

                    template_parser.add_argument(
                        "--variant",
                        help="template variant to use",
                        default='default',
                        choices=variants,
                    )

                    variables_path = os.path.join(entry.path, "variables.yaml")
                    with open(variables_path, 'r') as f:
                        variables = yaml.safe_load(f)
                    add_template_variables_to_parser(
                        template_parser, variables)

    return decorator


def add_template_variables_to_parser(parser, variables):
    args = variables.get('args', None)
    if args is None:
        args = {}
    for arg in args:
        long_option = arg.lower().replace("_", "-")
        long_option = f"--{long_option}"
        kwargs = variables['args'].get(arg, None)
        if kwargs is None:  # guard against explicit Nones in config
            kwargs = {}
        kwargs['required'] = kwargs.get('required', True)
        parser.add_argument(long_option, **kwargs)


def arg(*args, **kwargs):
    """Argument packaging function for command decorator"""
    return ([*args], kwargs)
