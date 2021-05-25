from argparse import ArgumentParser

_PARSER = ArgumentParser()
_PARSER.add_argument("--log_level", help="Specify log level", type=str,
                     choices=["debug", "info", "warning", "error", "critical"],
                     default="info")
_COMMANDS_PARSER = _PARSER.add_subparsers(title="commands", dest="command")


def command(args=[], parent=_COMMANDS_PARSER):
    """
    Decorator for CLI commands. 

    see commands.py for examples.
    """
    def decorator(func):
        parser = parent.add_parser(func.__name__, description=func.__doc__)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)
    return decorator


def arg(*args, **kwargs):
    """Argument packaging function for command decorator"""
    return ([*args], kwargs)
