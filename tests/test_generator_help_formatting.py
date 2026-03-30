import argparse

import pytest

from argcomplete_fish.generator import generate_fish_completions


def test_generate_help_with_substitutions():
    p = argparse.ArgumentParser(prog="mycmd")
    p.add_argument("--foo", default="bar", help="Foo option (default: %(default)s)")
    p.add_argument("--baz", type=int, default=42, help="Baz option type %(type)s")

    script = generate_fish_completions(p, "mycmd")

    assert '-d "Foo option (default: bar)"' in script
    assert '-d "Baz option type int"' in script


def test_generate_help_with_metavar():
    p = argparse.ArgumentParser(prog="mycmd")
    p.add_argument("--foo", metavar="FOO_VAL", help="Foo option (metavar: %(metavar)s)")

    script = generate_fish_completions(p, "mycmd")

    assert '-d "Foo option (metavar: FOO_VAL)"' in script


def test_invalid_help_format_fails():
    p = argparse.ArgumentParser(prog="mycmd")
    p.add_argument("--foo", help="Foo with missing key %(missing)s")

    with pytest.raises(KeyError, match="missing"):
        generate_fish_completions(p, "mycmd")
