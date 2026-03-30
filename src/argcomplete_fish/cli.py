import os
import sys
from argparse import ArgumentParser
from pathlib import Path

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
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "-o",
        "--output",
        help="Optional file path to write the completions to (overwrites). "
        "If no output option is provided, prints to stdout.",
    )
    output_group.add_argument(
        "-a",
        "--append",
        help="Optional file path to append the completions to.",
    )
    output_group.add_argument(
        "--auto-save",
        action="store_true",
        help="Automatically save the completions to the fish completions directory "
        "($XDG_CONFIG_HOME/fish/completions/<name>.fish or "
        "~/.config/fish/completions/<name>.fish).",
    )

    parser.add_argument(
        "--print",
        action="store_true",
        dest="force_print",
        help="Force print the completions to stdout, "
        "even if an output file is specified.",
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

    command_name = args.name
    if not command_name:
        inferred_name = target_parser.prog.strip()
        if inferred_name in (
            "argcomplete-fish",
            "cli.py",
            "python -m src.argcomplete_fish.cli",
            "",
        ):
            print(
                "Warning: Could not infer a meaningful command name from the parser "
                f"({inferred_name}).\n"
                "Please provide one with --name.",
                file=sys.stderr,
            )
            command_name = "unknown_command"
        else:
            command_name = inferred_name

    completions = generate_fish_completions(target_parser, command_name)

    output_path = None
    mode = "w"

    if args.auto_save:
        xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config_home:
            config_home = Path(xdg_config_home)
        else:
            config_home = Path.home() / ".config"
        completions_dir = config_home / "fish" / "completions"
        completions_dir.mkdir(parents=True, exist_ok=True)
        output_path = completions_dir / f"{command_name}.fish"
    elif args.output:
        output_path = Path(args.output)
    elif args.append:
        output_path = Path(args.append)
        mode = "a"

    if output_path:
        with output_path.open(mode) as f:
            f.write(completions)
            f.write("\n")

    if not output_path or args.force_print:
        print(completions)


if __name__ == "__main__":
    main()
