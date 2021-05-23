from argparse import ArgumentParser

PARSER = ArgumentParser()
COMMANDS_PARSER = PARSER.add_subparsers(title="commands", dest="command")


def command(args=[], parent=COMMANDS_PARSER):
    def decorator(func):
        parser = parent.add_parser(func.__name__, description=func.__doc__)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)
    return decorator


def arg(*args, **kwargs):
    return ([*args], kwargs)
