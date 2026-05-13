# Installing dependencies

You will need [uv](https://docs.astral.sh/uv/getting-started/installation/) and [git](https://git-scm.com/install/linux) installed on your system.

# Building kicad-python

First, run `git submodule update --init` to add KiCad's source code as a submodule.

NOTE: We recommend that you run `git config submodule.recurse true` in this repo so that
      when you run `git pull` in the future, the submodule will be kept up-to-date.

Then, install the project dependencies and generate the protobuf bindings by running:

```sh
uv sync
```

You can package the project and generate a Python wheel by running:

```sh
uv build
```

# Running examples

With KiCad running and the API server enabled in Preferences > Plugins, you should be able to run:

```sh
uv run examples/hello.py
```

This will work if you have a KiCad instance running, with the API server enabled,
and the server is listening at the default location (which will be the case if there
are no other instances of KiCad open at the time).

# Testing changes

Before committing, run the following commands to lint, type-check, and test the code:

```sh
uv run ruff check --exclude kicad
uv run mypy -p kipy
uv run pytest tests
```

