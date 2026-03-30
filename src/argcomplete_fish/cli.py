import sys
from argparse import ArgumentParser

from .generator import generate_fish_completions
from .inspector import load_parser


def get_cli_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="argcomplete-fish",
        description="Generate fish shell completions for Python argparse parsers.",
    )
    parser.add_argument(
        "target",
        help="Python path to the parser "
        "(e.g., 'my_module:parser' or 'my_package.module:get_parser').",
    )
    parser.add_argument(
        "-n",
        "--name",
        help="The name of the CLI command to generate completions for. "
        "If omitted, it will be inferred from the target parser's `prog` attribute.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Optional file path to write the completions to (overwrites). "
        "If neither -o nor -a is provided, prints to stdout.",
    )
    parser.add_argument(
        "-a",
        "--append",
        help="Optional file path to append the completions to.",
    )
    return parser


def main() -> None:
    parser = get_cli_parser()
    args = parser.parse_args()

    try:
        target_parser = load_parser(args.target)
    except Exception as e:
        print(f"Error loading parser from '{args.target}': {e}", file=sys.stderr)
        sys.exit(1)

    command_name = args.name or target_parser.prog
    if not command_name or command_name == "argparse":
        print(
            "Warning: Could not infer a meaningful command name from the parser. "
            "Please provide one with --name.",
            file=sys.stderr,
        )
        command_name = command_name or "unknown_command"

    completions = generate_fish_completions(target_parser, command_name)

    if args.output:
        with open(args.output, "w") as f:
            f.write(completions)
            f.write("\n")
    elif args.append:
        with open(args.append, "a") as f:
            f.write(completions)
            f.write("\n")
    else:
        print(completions)


if __name__ == "__main__":
    main()
