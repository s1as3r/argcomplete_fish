import os
import sys
from argparse import ArgumentParser
from importlib import import_module
from typing import cast


def load_parser(target: str) -> ArgumentParser:
    """
    Load an `ArgumentParser` from a string path ().

    ## Parameters
        target (str): string path to an Argument Parser (e.g: 'my_module:parser' or 'my_module:get_parser')

    ## Returns
        ArgumentParser: the loaded ArgumentParser object

    ## Raises
        ValueError: when the target string is not in the proper format
        ImportError: when the module could not be imported
        AttributeError: when the module does not contain the provided attribute
        TypeError: when the attribute is not/does not return an ArgumentParser
    """
    if ":" not in target:
        raise ValueError("Target must be in the format 'module.path:parser_name'")

    module_path, object_name = target.split(":", 1)

    # add current working directory to sys.path to allow loading local modules
    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.insert(0, cwd)
    if "" not in sys.path:
        sys.path.insert(0, "")

    try:
        module = import_module(module_path)
    except ImportError as e:
        raise ImportError(
            f"Could not import module '{module_path}'.\n\nUnderlying Error: {e}"
        )

    try:
        obj = module
        for part in object_name.split("."):
            obj = getattr(obj, part)
    except AttributeError:
        raise AttributeError(f"Module '{module_path}' has no attribute '{object_name}'")

    if callable(obj):
        obj = obj()

    if not isinstance(obj, ArgumentParser):
        raise TypeError(
            f"Target '{target}' is not an argparse.ArgumentParser (got {type(obj)})"
        )

    return cast(ArgumentParser, obj)
