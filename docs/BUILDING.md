# Building the Documentation

This guide covers how to build the kicad-python documentation locally.

## Prerequisites

Before building the documentation, you need to set up the development environment.

1. **Initialize the git submodule** (contains the protobuf definitions):

   ```bash
   git submodule update --init --recursive
   ```

2. **Install the protobuf compiler** (`protoc`):

   On macOS:
   ```bash
   brew install protobuf
   ```

   On Ubuntu/Debian:
   ```bash
   apt install protobuf-compiler
   ```

3. **Install Python build dependencies**:

   ```bash
   pip install "protoletariat==3.3.*" "mypy-protobuf==3.6.*"
   ```

4. **Generate the protobuf Python files**:

   ```bash
   python tools/generate_protos.py
   ```

5. **Install the package and documentation dependencies**:

   ```bash
   pip install -e .
   pip install sphinx furo
   ```

   Ensure the `protobuf` Python package version matches your `protoc` version. For `protoc` 33.x, use:

   ```bash
   pip install "protobuf>=6.0"
   ```

## Building

From the repository root, run:

```bash
sphinx-build -b html docs docs/_build
```

Or using the Makefile:

```bash
cd docs
make html
```

The generated HTML documentation will be in `docs/_build/`.

## Troubleshooting

### ModuleNotFoundError: No module named 'kipy.proto.common.envelope_pb2'

This error means the protobuf files haven't been generated. Run:

```bash
python tools/generate_protos.py
```

### Protobuf version mismatch error

If you see an error about mismatched Protobuf Gencode/Runtime versions, ensure your Python `protobuf` package version matches your `protoc` compiler version.

Check versions with:

```bash
protoc --version
python -c "import google.protobuf; print(google.protobuf.__version__)"
```

For `protoc` 33.x, install `protobuf>=6.0`. For older `protoc` versions (e.g., 25.x), use `protobuf>=4.25,<5`.
