# Copyright The KiCad Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pytest

from kipy.common_types import Rectangle, Text
from kipy.geometry import Vector2
from kipy.schematic_types import (
    SchematicField,
    SchematicGraphicShape,
    SchematicPin,
    SchematicSymbol,
    SchematicSymbolChild,
    SchematicText,
    SchematicTextBox,
)


def test_symbol_child_round_trip_all_types():
    definition = SchematicSymbol()
    definition.add_item(SchematicPin())
    definition.add_item(SchematicField())
    definition.add_item(SchematicGraphicShape())
    definition.add_item(SchematicText())
    definition.add_item(SchematicTextBox())

    restored = SchematicSymbol(proto=definition.proto)
    assert [type(child.item) for child in restored.items] == [
        SchematicPin,
        SchematicField,
        SchematicGraphicShape,
        SchematicText,
        SchematicTextBox,
    ]


def test_symbol_add_item_wraps_concrete_items():
    definition = SchematicSymbol()
    pin = SchematicPin()
    definition.add_item(pin)
    assert len(definition.items) == 1
    assert type(definition.items[0]) is SchematicSymbolChild
    assert definition.items[0].item is pin
    assert definition.items[0].unit is None
    assert not definition.items[0].is_private

    definition.add_item(SchematicPin(), unit=2, is_private=True)
    wrapped = definition.items[1]
    assert type(wrapped) is SchematicSymbolChild
    assert wrapped.unit == 2
    assert wrapped.is_private

    child = SchematicSymbolChild()
    child.item = SchematicPin()
    definition.add_item(child, unit=3, is_private=True)
    assert definition.items[2] is child
    assert child.unit == 3
    assert child.is_private


def test_symbol_child_rejects_bare_graphic_shapes():
    definition = SchematicSymbol()
    with pytest.raises(TypeError):
        definition.add_item(Rectangle.from_coords(Vector2.from_xy(0, 0), Vector2.from_xy(1, 1)))
    with pytest.raises(TypeError):
        definition.add_item(Text())

    child = SchematicSymbolChild()
    with pytest.raises(TypeError):
        child.item = Rectangle.from_coords(Vector2.from_xy(0, 0), Vector2.from_xy(1, 1))
