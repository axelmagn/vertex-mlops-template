from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

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
                    dest="config_files",
                    default=[])
PARSER.add_argument("--config-string",
                    help="configuration string to load.  May be repeated. "
                    + "Loaded after configuration files.",
                    action="append",
                    dest="config_strings",
                    default=[])
PARSER.add_argument("--out-file", type=str, default=None,
                    help="Output file (default: stdout)")

COMMANDS_PARSER = PARSER.add_subparsers(title="commands", dest="command")


def init_global_args(args):
    global _ARGS
    _ARGS = args


def get_args():
    global _ARGS
    return _ARGS


def command(args=[], parent=COMMANDS_PARSER, arg_parents=[PARSER]):
    """Decorator to denote functions that act as CLI commands."""
    def decorator(func):
        parser = parent.add_parser(
            func.__name__,
            description=func.__doc__,
            formatter_class=ArgumentDefaultsHelpFormatter,
            # parents=arg_parents,
        )
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)
        return func
    return decorator


def task(args=[]):
    """
    Tasks are standalone functions that have a corresponding argument parser.  

    Unlike commands, tasks are not integrated into the application's 
    command parsing tree. they are intended to be invoked programatically.  
    This is especially useful for training functions, where multiple 
    `train(...)` functions would inevitably lead to naming collisions, but each 
    defines its own set of hyperparameters.

    A task function's parser may be accessed via its `parser` attribute.
    """
    def decorator(func):
        parser = ArgumentParser(
            func.__name__,
            description=func.__doc__,
            formatter_class=ArgumentDefaultsHelpFormatter,
        )
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        func.parser = parser
        return func

    return decorator


def arg(*args, **kwargs):
    """Utility function used in defining command args."""
    return ([*args], kwargs)
