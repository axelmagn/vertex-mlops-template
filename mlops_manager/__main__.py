import logging

from . import cli, commands


def main():
    # parse arguments
    args, tail = cli._PARSER.parse_known_args()

    # configure logging
    log_level_num = getattr(logging, args.log_level.upper(), None)
    logging.basicConfig(level=log_level_num)

    # handle command
    if args.command is None:
        cli._PARSER.print_help()
    else:
        args.func(args, tail)


if __name__ == "__main__":
    main()
