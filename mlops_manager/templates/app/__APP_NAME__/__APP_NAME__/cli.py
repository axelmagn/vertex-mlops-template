from argparse import ArgumentParser

PARSER = ArgumentParser()
PARSER.add_argument("--log_level", type=str,
                    help="level of detail during logging",
                    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                    default="INFO")
PARSER.add_argument(
    "--build_dir", help="output directory for build targets.", default="./build")
PARSER.add_argument(
    "--config_dir", help="configuration root directory", default="./config")
PARSER.add_argument(
    "--deployment", help="configuration environment")

COMMANDS_PARSER = PARSER.add_subparsers(title="commands", dest="command")


def command(args=[], parent=COMMANDS_PARSER):
    # TODO(axelmagn): docstring
    def decorator(func):
        parser = parent.add_parser(func.__name__, description=func.__doc__)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)
    return decorator


def arg(*args, **kwargs):
    # TODO(axelmagn): docstring
    return ([*args], kwargs)
