# argcomplete_fish
*Fish shell tab completions for Python argparse*

`argcomplete_fish` generates static [Fish shell](https://fishshell.com/) completion
scripts for Python applications that use the standard [`argparse`](https://docs.python.org/3/library/argparse.html) module.

## Features

* **Zero Latency**: Generates native Fish completion commands (`complete -c ...`) so completions load instantly without executing Python.
* **No Code Modifications Required**: You do not need to add any markers to your application code.
* **Rich Completions**: Automatically extracts flags, subcommands, positional arguments, `choices`, and help text from your `argparse` configuration.
* **Auto-installation**: Automatically save completions directly to your Fish configuration directory (`~/.config/fish/completions/`).

## Synopsis

> [!NOTE]
> Since `argcomplete_fish` loads your module to inspect the parser, you should
ideally run `argcomplete-fish` from within the same virtual environment or
context as your application to ensure all dependencies are available.

To generate completions, you simply pass the Python path to your `ArgumentParser` instance (or a function that returns one) to the `argcomplete-fish` CLI.

For example, if you have a file `my_app/cli.py` with:

```python
import argparse

def get_parser():
    parser = argparse.ArgumentParser(prog="my_app", description="My awesome app")
    parser.add_argument("--verbose", action="store_true", help="Increase verbosity")
    parser.add_argument("--mode", choices=["fast", "slow"], help="Execution mode")
    return parser
```

You can generate and install the Fish completions in one step:

```bash
argcomplete-fish "my_app.cli:get_parser" --auto-save
```

This will automatically create `~/.config/fish/completions/my_app.fish`. Next time you open Fish,
typing `my_app <TAB>` will be instantly completed with your arguments, choices, and help strings!

<details>
<summary>Output options</summary>

If you prefer to review the completion script or distribute it with your package,
you can use the output flags:

* **Print to stdout (default):**
  ```bash
  argcomplete-fish "my_app.cli:get_parser"
  ```
* **Write to a specific file:**
  ```bash
  argcomplete-fish "my_app.cli:get_parser" -o completions/my_app.fish
  ```
* **Append to a file:**
  ```bash
  argcomplete-fish "my_app.cli:get_parser" -a completions/existing.fish
  ```
* **Override the command name:**
  *(Useful if your script's entry point is named differently than the parser's `prog` attribute)*
  ```bash
  argcomplete-fish "my_app.cli:get_parser" --name my-custom-cmd
  ```
</details>
