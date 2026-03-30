import argparse

import pytest

from argcomplete_fish.inspector import load_parser


def my_parser():
    return argparse.ArgumentParser(prog="my_prog")


parser = argparse.ArgumentParser(prog="my_global")


class MyClass:
    parser = argparse.ArgumentParser(prog="my_class_prog")

    @staticmethod
    def get_parser():
        return argparse.ArgumentParser(prog="my_class_static_prog")


def test_load_parser_invalid_format():
    with pytest.raises(ValueError, match="Target must be in the format"):
        load_parser("invalid_target")


def test_load_parser_missing_module():
    with pytest.raises(ImportError, match="Could not import module"):
        load_parser("non_existent_module:parser")


def test_load_parser_missing_attribute():
    with pytest.raises(AttributeError, match="has no attribute"):
        load_parser("tests.test_inspector:non_existent_parser")


def test_load_parser_missing_nested_attribute():
    with pytest.raises(AttributeError, match="has no attribute"):
        load_parser("tests.test_inspector:MyClass.non_existent")


def test_load_parser_invalid_type():
    with pytest.raises(TypeError, match="is not an argparse.ArgumentParser"):
        load_parser("tests.test_inspector:MyClass")


def test_load_parser_global_variable():
    p = load_parser("tests.test_inspector:parser")
    assert isinstance(p, argparse.ArgumentParser)
    assert p.prog == "my_global"


def test_load_parser_function():
    p = load_parser("tests.test_inspector:my_parser")
    assert isinstance(p, argparse.ArgumentParser)
    assert p.prog == "my_prog"


def test_load_parser_nested_attribute():
    p = load_parser("tests.test_inspector:MyClass.parser")
    assert isinstance(p, argparse.ArgumentParser)
    assert p.prog == "my_class_prog"


def test_load_parser_nested_function():
    p = load_parser("tests.test_inspector:MyClass.get_parser")
    assert isinstance(p, argparse.ArgumentParser)
    assert p.prog == "my_class_static_prog"
