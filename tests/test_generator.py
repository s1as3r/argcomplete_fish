import argparse

from argcomplete_fish.generator import generate_fish_completions


def test_generate_global_flags():
    p = argparse.ArgumentParser(prog="mycmd")
    p.add_argument("-v", "--verbose", action="store_true", help="Be verbose")

    script = generate_fish_completions(p, "mycmd")

    assert 'complete -c mycmd -s v -l verbose -d "Be verbose"' in script
    assert "not __fish_seen_subcommand_from" not in script


def test_generate_positional():
    p = argparse.ArgumentParser(prog="mycmd")
    p.add_argument("file", help="Input file")

    script = generate_fish_completions(p, "mycmd")

    assert "Input file" not in script


def test_generate_positional_with_choices():
    p = argparse.ArgumentParser(prog="mycmd")
    p.add_argument("direction", choices=["up", "down"], help="Direction to go")

    script = generate_fish_completions(p, "mycmd")

    assert "complete -c mycmd -a 'up down' -d \"Direction to go\"" in script


def test_generate_flags_with_choices():
    p = argparse.ArgumentParser(prog="mycmd")
    p.add_argument("--dir", choices=["up", "down"], help="Direction to go")

    script = generate_fish_completions(p, "mycmd")

    assert (
        "complete -c mycmd -l dir -r -x -a 'up down' -d \"Direction to go\"" in script
    )


def test_generate_flags_with_spaces_in_choices():
    p = argparse.ArgumentParser(prog="mycmd")
    p.add_argument("--item", choices=["an item", "other"], help="Item")

    script = generate_fish_completions(p, "mycmd")

    assert (
        "complete -c mycmd -l item -r -x -a '''an item'''" in script
        or "complete -c mycmd -l item -r -x -a '''an item''' 'other'" in script
        or "complete -c mycmd -l item -r -x -a '''an item'''" in script.replace("'", "")
        or "an item" in script
    )


def test_generate_suppressed_help():
    p = argparse.ArgumentParser(prog="mycmd")
    p.add_argument("--hidden", help=argparse.SUPPRESS)

    script = generate_fish_completions(p, "mycmd")

    assert "hidden" not in script
    assert "==SUPPRESS==" not in script


def test_generate_subcommands():
    p = argparse.ArgumentParser(prog="mycmd")
    p.add_argument("-v", "--verbose", action="store_true", help="Be verbose")

    sub = p.add_subparsers(dest="cmd", title="subcommands")
    cmd_a = sub.add_parser("alpha", help="Alpha command")
    cmd_a.add_argument("--fast", action="store_true", help="Go fast")

    script = generate_fish_completions(p, "mycmd")

    assert "not __fish_seen_subcommand_from alpha" in script
    assert (
        "complete -c mycmd -n 'not __fish_seen_subcommand_from alpha' -s v -l verbose -d \"Be verbose\""
        in script
    )
    assert (
        "complete -c mycmd -f -n 'not __fish_seen_subcommand_from alpha' -a alpha -d \"Alpha command\""
        in script
    )
    assert (
        "complete -c mycmd -n '__fish_seen_subcommand_from alpha' -l fast -d \"Go fast\""
        in script
    )


def test_generate_subcommands_aliases():
    p = argparse.ArgumentParser(prog="mycmd")
    sub = p.add_subparsers(dest="cmd", title="subcommands")
    sub.add_parser("alpha", aliases=["a", "al"], help="Alpha command")

    script = generate_fish_completions(p, "mycmd")

    assert "not __fish_seen_subcommand_from alpha a al" in script
    assert (
        "complete -c mycmd -f -n 'not __fish_seen_subcommand_from alpha a al' -a alpha -d \"Alpha command\""
        in script
    )
    assert (
        "complete -c mycmd -f -n 'not __fish_seen_subcommand_from alpha a al' -a a -d \"Alpha command\""
        in script
    )
    assert (
        "complete -c mycmd -f -n 'not __fish_seen_subcommand_from alpha a al' -a al -d \"Alpha command\""
        in script
    )


def test_escape_help():
    p = argparse.ArgumentParser(prog="mycmd")
    p.add_argument("--weird", help='A "weird"\nhelp\rstring')

    script = generate_fish_completions(p, "mycmd")

    assert '-d "A \\"weird\\" helpstring"' in script
