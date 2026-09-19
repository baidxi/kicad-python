# Copyright The KiCad Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM
# THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Fixtures and opt-in mechanism for tests that talk to a headless KiCad.

Live tests are skipped unless all of the following are true:

- A ``kicad-cli`` binary is available: either the ``KICAD_CLI`` environment
  variable (usually set in a gitignored ``.env`` file at the repo root) points
  at the binary, or one is found in the default install locations or on PATH.
- The ``--live`` pytest flag is passed (or ``KIPY_TEST_LIVE=1`` is set in the
  environment).

Usage::

    KICAD_CLI=/path/to/kicad-cli pytest --live tests/test_live_board.py
"""

from __future__ import annotations

import os
import pathlib
import tempfile

import pytest

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = lambda *_args, **_kwargs: False

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]

if load_dotenv is not None:
    load_dotenv(REPO_ROOT / ".env")


def _find_kicad_cli() -> str | None:
    """Resolve kicad-cli from KICAD_CLI, the repo .env, or the default locations."""
    hint = os.environ.get("KICAD_CLI")
    if hint:
        hint = os.path.expanduser(hint)
        if os.access(hint, os.X_OK):
            return hint
        return None

    from kipy.server import find_kicad_cli

    try:
        return find_kicad_cli(None)
    except FileNotFoundError:
        return None


def pytest_addoption(parser: pytest.Parser):
    group = parser.getgroup("kipy-live")
    group.addoption(
        "--live",
        action="store_true",
        default=False,
        help="Run live tests against a headless kicad-cli (requires KICAD_CLI or a discoverable kicad-cli)",
    )
    parser.addini(
        "live_kicad_cli",
        help="Path to kicad-cli used by live tests (overridden by the KICAD_CLI environment variable)",
        default="",
    )


def pytest_configure(config: pytest.Config):
    config.addinivalue_line(
        "markers",
        "live: test talks to a live, headless KiCad via kicad-cli (deselected unless --live)",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]):
    if config.getoption("--live"):
        return

    skip_live = pytest.mark.skip(reason="live test: pass --live and set KICAD_CLI to run")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)


def _supports_api_server(cli_path: str) -> bool:
    """True when the binary implements the api-server subcommand."""
    import subprocess

    try:
        proc = subprocess.run(
            [cli_path, "api-server", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False

    output = proc.stdout + proc.stderr
    return "api-server" in output


@pytest.fixture(scope="session")
def kicad_cli(pytestconfig: pytest.Config) -> str:
    """Path to a kicad-cli binary capable of running the API server.

    Skips the live tests when no usable binary is available.
    """
    path = os.environ.get("KICAD_CLI") or pytestconfig.getini("live_kicad_cli")
    if not path:
        path = _find_kicad_cli() or ""
    if path:
        path = os.path.expanduser(path)
    if not path or not os.access(path, os.X_OK):
        pytest.skip("kicad-cli not found (set KICAD_CLI or install KiCad)")
    if not _supports_api_server(path):
        pytest.skip(f"kicad-cli at {path} does not support the api-server subcommand")
    return path


@pytest.fixture(scope="session")
def kicad(kicad_cli: str):
    """A shared connection to a headless kicad-cli API server for the whole session."""
    from kipy import KiCad

    with KiCad(headless=True, kicad_cli_path=kicad_cli) as k:
        yield k


@pytest.fixture(scope="session")
def server_api_version(kicad) -> tuple[int, ...]:
    """(major, minor) of the connected KiCad, for version-gated tests."""
    version = kicad.get_version()
    return (version.major, version.minor)


@pytest.fixture
def board(kicad):
    """An empty board document on the shared headless server."""
    from kipy.proto.common.types import DocumentType

    path = os.path.join(tempfile.mkdtemp(prefix="kipy-live-"), "live.kicad_pcb")
    kicad.create_document(path, DocumentType.DOCTYPE_PCB)
    doc = kicad.get_board().document
    try:
        yield kicad.get_board()
    finally:
        kicad.close_document(doc)


@pytest.fixture
def schematic(kicad):
    """An empty schematic document on the shared headless server."""
    from kipy.proto.common.types import DocumentType

    path = os.path.join(tempfile.mkdtemp(prefix="kipy-live-"), "live.kicad_sch")
    kicad.create_document(path, DocumentType.DOCTYPE_SCHEMATIC)
    doc = kicad.get_schematic().document
    try:
        yield kicad.get_schematic()
    finally:
        kicad.close_document(doc)
