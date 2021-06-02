from argparse import ArgumentParser

PARSER = ArgumentParser()
PARSER.add_argument("--log-level", type=str,
                    help="level of detail during logging",
                    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                    default="INFO")
PARSER.add_argument("--build-dir",
                    help="output directory for build targets.",
                    default="./build")
PARSER.add_argument("-c", "--config-file",
                    help="configuration file to load.  May be repeated.",
                    action="append",
                    dest="config_files")

COMMANDS_PARSER = PARSER.add_subparsers(title="commands", dest="command")


def init_global_args(args):
    global _ARGS
    _ARGS = args


def get_args():
    global _ARGS
    return _ARGS


def command(args=[], parent=COMMANDS_PARSER):
    """Decorator to denote functions that act as CLI commands."""
    def decorator(func):
        parser = parent.add_parser(func.__name__, description=func.__doc__)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)
    return decorator


def arg(*args, **kwargs):
    """Utility function used in defining command args."""
    return ([*args], kwargs)
