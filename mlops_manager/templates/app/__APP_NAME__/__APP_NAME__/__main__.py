import logging

from . import cli, commands


def main():
    # parse arguments
    args = cli.PARSER.parse_args()

    # configure logging
    log_level_num = getattr(logging, args.log_level.upper(), None)
    logging.basicConfig(level=log_level_num)

    # handle command
    if args.command is None:
        cli.PARSER.print_help()
    else:
        args.func(args)


if __name__ == "__main__":
    main()
