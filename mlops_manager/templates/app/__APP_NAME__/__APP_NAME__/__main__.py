import logging

from . import commands  # even if unused, this loads commands into parser
from . import cli, config


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
        # load config globally
        config.init_global_config(args.config_files)
        # invoke command
        args.func(args)


if __name__ == "__main__":
    main()
