# ignore-flake8-error

Add `noqa` comments to ignore every occurrence of a flake8 error.

## Usage

Install with pip:

```shell
python -m pip install ignore-flake8-error
```

Call the tool with an error code you want to add ignore comments for and the paths tothe files:

```shell
ignore-flake8-error F401 path/to/files/ path/to/more/files/s
```

## Rationale

When adding a new plugin (or enabling more rules) to flake8 on a large codebase,
fixing the existing violations can be too large a task to do quickly. However,
starting to check the rule sooner will prevent new violations fom being
introduces.

Ignoring existing violation is a quick wya to allow new rules to be enabled. You
can then burn down the existing violations over time.

This tool makes it easy to find and ignore all current violations of a rule so
that it can be enabled.
