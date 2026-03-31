import argparse
import shlex
from logging import getLogger

logger = getLogger(__name__)


def _escape_help(text: str) -> str:
    """Escape a help string for Fish."""
    if not text:
        return ""
    text = text.replace("\n", " ").replace("\r", "").replace('"', r"\"")
    return text


def _generate_action_completion(
    cmd_name: str,
    action: argparse.Action,
    condition: str = "",
    formatter: argparse.HelpFormatter | None = None,
) -> list[str]:
    """Generate Fish completion commands for a single argparse action."""
    logger.debug(
        f"Processing action: dest={action.dest!r}, "
        f"option_strings={action.option_strings}, "
        f"nargs={action.nargs!r}, choices={action.choices}"
    )

    commands = []
    flags = []

    # determine flags (-s, -l)
    has_opts = bool(action.option_strings)
    for opt_str in action.option_strings:
        if opt_str.startswith("--"):
            flags.append(f"-l {shlex.quote(opt_str[2:])}")
        elif opt_str.startswith("-"):
            flags.append(f"-s {shlex.quote(opt_str[1:])}")

    # determine if it requires an argument
    takes_arg = (
        action.nargs is None
        or (isinstance(action.nargs, int) and action.nargs > 0)
        or action.nargs
        in [argparse.OPTIONAL, argparse.ONE_OR_MORE, argparse.ZERO_OR_MORE]
    )

    if takes_arg and has_opts:
        flags.append("-r")

    # check choices
    choices_str = ""
    if action.choices:
        choices_str = " ".join(shlex.quote(str(c)) for c in action.choices)
        if has_opts:
            flags.append(
                "-x"
            )  # exclusive: no file completion since choices are provided
            flags.append(f"-a {shlex.quote(choices_str)}")

    if action.help == argparse.SUPPRESS:
        logger.debug(f"Action suppressed: dest={action.dest!r}")
        return []

    help_raw = action.help if action.help and isinstance(action.help, str) else ""
    if help_raw and formatter:
        help_raw = formatter._expand_help(action)

    help_str = _escape_help(help_raw)
    if help_str:
        flags.append(f'-d "{help_str}"')

    flags_str = " ".join(flags)
    cond_str = f"-n {shlex.quote(condition)} " if condition else ""

    if has_opts:
        cmd = f"complete -c {shlex.quote(cmd_name)} {cond_str}{flags_str}"
        logger.debug(f"Generated option command: {cmd}")
        commands.append(cmd)
    # positional argument
    elif action.choices:
        cmd = (
            f"complete -c {shlex.quote(cmd_name)} {cond_str}-a "
            f'{shlex.quote(choices_str)} -d "{help_str}"'
        )
        logger.debug(f"Generated positional choices command: {cmd}")
        commands.append(cmd)
    else:
        logger.debug("Skipped action (no options or choices)")

    return commands


def _generate_subcommand_completions(
    command_name: str,
    subparsers_action: argparse._SubParsersAction,
    global_cond: str,
    help_formatter: argparse.HelpFormatter | None,
) -> list[str]:
    """Generate Fish completion commands for subcommands."""
    lines = []
    lines.append("")
    lines.append("# Subcommands")

    help_by_subcmd = {}
    if hasattr(subparsers_action, "_choices_actions"):
        for act in subparsers_action._choices_actions:
            help_by_subcmd[act.dest] = act.help

    # we can determine aliases by mapping subparser instances to their first known dest
    parser_to_help = {}
    if hasattr(subparsers_action, "_choices_actions"):
        for act in subparsers_action._choices_actions:
            if (
                hasattr(subparsers_action, "choices")
                and act.dest in subparsers_action.choices
            ):
                parser_to_help[id(subparsers_action.choices[act.dest])] = act.help

    if hasattr(subparsers_action, "choices") and subparsers_action.choices:
        for subcmd_name, subparser in subparsers_action.choices.items():
            logger.debug(f"Processing subcommand: {subcmd_name!r}")
            help_str = help_by_subcmd.get(
                subcmd_name,
                parser_to_help.get(
                    id(subparser), getattr(subparser, "description", "") or ""
                ),
            )

            help_str = _escape_help(help_str)
            help_flag = f'-d "{help_str}"' if help_str else ""

            cond_str = f"-n {shlex.quote(global_cond)} " if global_cond else ""
            lines.append(
                f"complete -c {shlex.quote(command_name)} -f {cond_str}-a "
                f"{shlex.quote(subcmd_name)} {help_flag}"
            )

            cond = f"__fish_seen_subcommand_from {shlex.quote(subcmd_name)}"
            if hasattr(subparser, "_actions"):
                for action in subparser._actions:
                    for cmd in _generate_action_completion(
                        command_name,
                        action,
                        condition=cond,
                        formatter=help_formatter,
                    ):
                        lines.append(cmd)

    return lines


def generate_fish_completions(
    parser: argparse.ArgumentParser, command_name: str
) -> str:
    """
    Generate the Fish completion script for an ArgumentParser.

    ## Parameters
        parser (ArgumentParser): parser to generate the completion script for.
        command_name (str): command name to use for completions

    ## Returns
        str: the fish completion script
    """
    if not command_name:
        command_name = parser.prog

    logger.debug(f"Starting Fish completion generation for command: {command_name!r}")

    lines = []
    lines.append(f"# Fish completions for {command_name}")
    lines.append("# Generated by argcomplete-fish")
    lines.append("")

    # first, separate global actions from subparsers
    global_actions = []
    subparsers_action = None

    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            subparsers_action = action
        else:
            global_actions.append(action)

    # condition for global options: "not __fish_seen_subcommand_from sub1 sub2"
    global_cond = ""
    if subparsers_action and subparsers_action.choices:
        all_subcmds = " ".join(shlex.quote(k) for k in subparsers_action.choices.keys())
        global_cond = f"not __fish_seen_subcommand_from {all_subcmds}"

    # generate global options
    help_formatter = parser._get_formatter()
    for action in global_actions:
        for cmd in _generate_action_completion(
            command_name,
            action,
            condition=global_cond,
            formatter=help_formatter,
        ):
            lines.append(cmd)

    # generate subcommands
    if (
        subparsers_action
        and hasattr(subparsers_action, "choices")
        and subparsers_action.choices
    ):
        lines.extend(
            _generate_subcommand_completions(
                command_name, subparsers_action, global_cond, help_formatter
            )
        )

    return "\n".join(lines)
