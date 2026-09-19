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

"""Live tests for geometry views and item moves on schematics.

Companion to ``test_live_board.py``; same opt-in rules apply (``pytest --live``
plus a usable ``kicad-cli``).  See ``tests/conftest.py``.
"""

import pytest

from kipy.geometry import Vector2
from kipy.schematic_types import SchematicLine, SchematicText

pytestmark = pytest.mark.live


def _fetch_text(schematic, text: SchematicText) -> SchematicText:
    fetched = [item for item in schematic.get_items() if item.id == text.id]
    assert len(fetched) == 1
    return fetched[0]


def _fetch_line(schematic, line: SchematicLine) -> SchematicLine:
    fetched = [item for item in schematic.get_items() if item.id == line.id]
    assert len(fetched) == 1
    return fetched[0]


def test_schematic_text_position_view_is_mutable(schematic):
    """SchematicText.position returns a live view: mutating it in place must be
    visible locally and persist through update_items.

    KiCad snaps schematic text positions to the editor grid when an item is
    updated, so the test uses grid-aligned values.
    """
    text = SchematicText()
    text.value = "view test"
    created = schematic.create_items(text)[0]
    assert created.position == Vector2.from_xy(0, 0)

    created.position.x = 1000
    created.position.y = 2000
    assert created.position == Vector2.from_xy(1000, 2000)

    schematic.update_items([created])
    fetched = _fetch_text(schematic, created)
    assert fetched.position == Vector2.from_xy(1000, 2000)


def test_schematic_text_position_view_supports_iadd(schematic):
    """+= on the position view mutates the underlying proto in place."""
    text = SchematicText()
    text.value = "iadd test"
    text.position = Vector2.from_xy(1000, 2000)
    created = schematic.create_items(text)[0]

    fetched = _fetch_text(schematic, created)
    fetched.position += Vector2.from_xy(1000, 2000)
    schematic.update_items([fetched])

    refetched = _fetch_text(schematic, created)
    assert refetched.position == Vector2.from_xy(2000, 4000)


def test_schematic_line_endpoints_view_is_mutable(schematic):
    """SchematicLine start/end are live views; mutating them persists."""
    line = SchematicLine()
    line.start = Vector2.from_xy(0, 0)
    line.end = Vector2.from_xy(10000, 0)
    created = schematic.create_items(line)[0]

    fetched = _fetch_line(schematic, created)
    fetched.end.x += 5000
    schematic.update_items([fetched])

    refetched = _fetch_line(schematic, created)
    assert refetched.start == Vector2.from_xy(0, 0)
    assert refetched.end == Vector2.from_xy(15000, 0)


def test_schematic_line_move_via_iadd(schematic):
    """Moving a line by += on both endpoints persists to KiCad."""
    line = SchematicLine()
    line.start = Vector2.from_xy(0, 0)
    line.end = Vector2.from_xy(10000, 0)
    created = schematic.create_items(line)[0]

    delta = Vector2.from_xy(2000, 3000)
    fetched = _fetch_line(schematic, created)
    fetched.start += delta
    fetched.end += delta
    schematic.update_items([fetched])

    refetched = _fetch_line(schematic, created)
    assert refetched.start == Vector2.from_xy(2000, 3000)
    assert refetched.end == Vector2.from_xy(12000, 3000)
