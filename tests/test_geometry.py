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
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import math

import pytest

from kipy.common_types import Circle
from kipy.geometry import (
    Box2,
    PolyLine,
    PolyLineNode,
    Vector2,
    arc_angle,
    arc_bounding_box,
    arc_center,
    normalize_angle_pi_radians,
)
from kipy.proto.board import board_types_pb2
from kipy.proto.common.types import base_types_pb2


def test_arc_center_circle():
    start = Vector2.from_xy(0, 0)
    mid = Vector2.from_xy(1, 1)
    end = Vector2.from_xy(0, 0)
    center = arc_center(start, mid, end)
    assert center == (start + mid) * 0.5


def test_arc_center_collinear():
    start = Vector2.from_xy(0, 0)
    mid = Vector2.from_xy(1, 1)
    end = Vector2.from_xy(2, 2)
    center = arc_center(start, mid, end)
    assert center is None


def test_arc_center_normal_case():
    start = Vector2.from_xy(1000, 0)
    mid = Vector2.from_xy(1500, 1000)
    end = Vector2.from_xy(1000, 2000)
    center = arc_center(start, mid, end)
    assert center is not None
    assert center.x == pytest.approx(250, rel=1e-2)
    assert center.y == pytest.approx(1000, rel=1e-2)


def test_arc_center_another_case():
    start = Vector2.from_xy(1000, 0)
    mid = Vector2.from_xy(0, 1000)
    end = Vector2.from_xy(-1000, 0)
    center = arc_center(start, mid, end)
    assert center is not None
    assert center.x == pytest.approx(0, rel=1e-2)
    assert center.y == pytest.approx(0, rel=1e-2)


def test_box2_merge():
    box1 = Box2.from_pos_size(Vector2.from_xy(0, 0), Vector2.from_xy(1000, 1000))
    box2 = Box2.from_pos_size(Vector2.from_xy(2000, 2000), Vector2.from_xy(1000, 1000))
    box1.merge(box2)
    assert box1.pos == Vector2.from_xy(0, 0)
    assert box1.size == Vector2.from_xy(3000, 3000)


def test_box2_inflate():
    box = Box2.from_pos_size(Vector2.from_xy(1000, 1000), Vector2.from_xy(1000, 1000))
    box.inflate(1000)
    assert box.pos == Vector2.from_xy(500, 500)
    assert box.size == Vector2.from_xy(2000, 2000)


def test_box2_inflate_negative():
    box = Box2.from_pos_size(Vector2.from_xy(1000, 1000), Vector2.from_xy(2000, 2000))
    box.inflate(-1000)
    assert box.pos == Vector2.from_xy(1500, 1500)
    assert box.size == Vector2.from_xy(1000, 1000)


def test_arc_angle_minor():
    """Test arc centered at (0,0), radius 1000, and a 90 degree angle."""
    start = Vector2.from_xy(1000, 0)
    mid = Vector2.from_xy(707, 707)
    end = Vector2.from_xy(0, 1000)
    angle = arc_angle(start, mid, end)
    assert angle == pytest.approx(math.pi / 2, rel=1e-2)


def test_arc_angle_major():
    """Test arc centered at (0, 0), radius 1000, and a 270 degree angle."""
    start = Vector2.from_xy(1000, 0)
    mid = Vector2.from_xy(-707, 707)
    end = Vector2.from_xy(0, -1000)
    angle = arc_angle(start, mid, end)
    assert angle == pytest.approx((3 / 2) * math.pi, rel=1e-2)


def test_arc_angle_full_circle():
    """Test arc centered at (0, 0), with start and end points equal"""
    start = Vector2.from_xy(-1000, 0)
    mid = Vector2.from_xy(1000, 0)
    end = Vector2.from_xy(-1000, 0)
    angle = arc_angle(start, mid, end)
    assert angle == pytest.approx(2 * math.pi, rel=1e-2)


def test_arc_angle_degenerate():
    """Test arc with start, mid, and end points all on the same line."""
    start = Vector2.from_xy(1000, 0)
    mid = Vector2.from_xy(2000, 0)
    end = Vector2.from_xy(3000, 0)
    angle = arc_angle(start, mid, end)
    assert angle is None


def test_arc_angle_zero():
    """Test arc with start, mid, and end points all the same."""
    start = Vector2.from_xy(1000, 0)
    mid = Vector2.from_xy(1000, 0)
    end = Vector2.from_xy(1000, 0)
    angle = arc_angle(start, mid, end)
    assert angle == 0


def test_normalize_angle_pi_radians():
    """Test normalization of angles to the range (-pi, pi]"""
    assert normalize_angle_pi_radians(0) == 0
    assert normalize_angle_pi_radians(math.pi) == math.pi
    assert normalize_angle_pi_radians(-math.pi) == math.pi
    assert normalize_angle_pi_radians(2 * math.pi) == 0
    assert normalize_angle_pi_radians(-2 * math.pi) == 0
    assert normalize_angle_pi_radians(math.pi / 2) == math.pi / 2
    assert normalize_angle_pi_radians(-math.pi / 2) == -math.pi / 2
    assert normalize_angle_pi_radians(3 * math.pi / 2) == -math.pi / 2
    assert normalize_angle_pi_radians(-3 * math.pi / 2) == math.pi / 2


def test_box2_construction():
    box1 = Box2.from_pos_size(Vector2.from_xy(1, 2), Vector2.from_xy(0, 0))
    box1.merge(Vector2.from_xy(3, 4))
    box2 = Box2.from_points([Vector2.from_xy(1, 2), Vector2.from_xy(3, 4)])
    assert box1.pos == box2.pos
    assert box1.size == box2.size


def test_seg_bounding_box():
    box = Box2.from_pos_size(Vector2.from_xy(1, 2), Vector2.from_xy(0, 0))
    box.merge(Vector2.from_xy(3, 4))
    assert box.pos == Vector2.from_xy(1, 2)
    assert box.size == Vector2.from_xy(2, 2)


def test_arc_bounding_box():
    start = Vector2.from_xy(10000, 0)
    mid = Vector2.from_xy(-7071, 7071)
    end = Vector2.from_xy(0, -10000)

    box = arc_bounding_box(start, mid, end)

    assert box.pos == Vector2.from_xy(-10000, -10000)
    # epsilon because we have a calculated center; won't exactly match KiCad due to rounding
    assert (box.size - Vector2.from_xy(20000, 20000)).length() < 2


def test_arc_bounding_box_long_sweep():
    start = Vector2.from_xy(5, 0)
    mid = Vector2.from_xy(0, 5)
    end = Vector2.from_xy(3, 4)

    box = arc_bounding_box(start, mid, end)

    assert box.pos == Vector2.from_xy(-5, -5)
    assert box.size == Vector2.from_xy(10, 10)


def test_arc_bounding_box_degenerate():
    start = Vector2.from_xy(1, 2)
    mid = Vector2.from_xy(2, 3)
    end = Vector2.from_xy(3, 4)

    box = arc_bounding_box(start, mid, end)

    assert box.pos == Vector2.from_xy(1, 2)
    assert box.size == Vector2.from_xy(2, 2)


def test_circle_bounding_box():
    proto = base_types_pb2.GraphicShape()
    proto.circle.center.x_nm = 10
    proto.circle.center.y_nm = 20
    proto.circle.radius_point.x_nm = 13
    proto.circle.radius_point.y_nm = 24

    box = Circle(proto).bounding_box()

    assert box.pos == Vector2.from_xy(5, 15)


def test_board_shape_proto_is_outer_message():
    """Board shapes mix two protos in one MRO: BoardShape holds the outer
    BoardGraphicShape while the GraphicShape base holds an inner GraphicShape.
    ``proto`` must resolve to the outer message, or wire serialization
    (create_items/update_items) sends the wrong type_url."""
    from kipy.board_types import (
        BoardArc,
        BoardBezier,
        BoardCircle,
        BoardPolygon,
        BoardRectangle,
        BoardSegment,
    )

    for cls in (BoardSegment, BoardArc, BoardCircle, BoardRectangle, BoardPolygon, BoardBezier):
        assert type(cls().proto) is board_types_pb2.BoardGraphicShape


def test_board_shape_wire_round_trip():
    """A board shape packed the way create_items packs it must unpack to the same
    concrete type with its geometry intact."""
    from kipy.board_types import BoardSegment, to_concrete_board_shape, unwrap
    from kipy.util import pack_any

    seg = BoardSegment()
    seg.start = Vector2.from_xy(1000, 2000)
    seg.end = Vector2.from_xy(3000, 4000)

    packed = pack_any(seg.proto)
    assert packed.type_url == "type.googleapis.com/kiapi.board.types.BoardGraphicShape"

    restored = to_concrete_board_shape(unwrap(packed))
    assert type(restored) is BoardSegment
    assert restored.start == Vector2.from_xy(1000, 2000)
    assert restored.end == Vector2.from_xy(3000, 4000)


def test_board_shape_clone():
    """Item.clone builds a new proto from self.proto; it must produce the outer
    BoardGraphicShape, not the inner GraphicShape."""
    from kipy.board_types import BoardSegment

    seg = BoardSegment()
    seg.start = Vector2.from_xy(1000, 0)
    seg.end = Vector2.from_xy(2000, 0)

    clone = seg.clone()
    assert type(clone._proto) is board_types_pb2.BoardGraphicShape
    assert not clone._proto.HasField("id")
    assert clone.start == seg.start


def test_board_polygon_from_rectangle():
    """from_rectangle copies the rectangle's outer proto into the polygon; the MRO
    shadowing bug made this raise a CopyFrom type mismatch."""
    from kipy.board_types import BoardPolygon, BoardRectangle

    rect = BoardRectangle()
    rect.top_left = Vector2.from_xy(0, 0)
    rect.bottom_right = Vector2.from_xy(2000, 3000)

    poly = BoardPolygon.from_rectangle(rect)
    assert type(poly._proto) is board_types_pb2.BoardGraphicShape
    outline = poly.polygons[0].outline
    assert outline.closed
    assert len(outline.nodes) == 4
    assert outline[0].point == rect.top_left
    assert outline[2].point == rect.bottom_right


def test_padstack_layer_custom_shapes_round_trip():
    """custom_shapes stores repeated BoardGraphicShape; the setter must accept board
    shape wrappers whose .proto is the outer message."""
    from kipy.board_types import BoardSegment, PadStackLayer

    layer = PadStackLayer()
    seg = BoardSegment()
    seg.start = Vector2.from_xy(0, 0)
    seg.end = Vector2.from_xy(1000, 0)

    layer.custom_shapes = [seg]
    assert type(layer._proto.custom_shapes[0]) is board_types_pb2.BoardGraphicShape
    assert layer.custom_shapes[0].start == seg.start


def test_graphic_shape_proto_is_inner_message():
    """Pure graphic shapes (no board wrapper in the MRO) must expose the inner
    GraphicShape proto; schematic code serializes it directly."""
    from kipy.common_types import GraphicShape, Polygon, Rectangle

    rect = Rectangle.from_coords(Vector2.from_xy(0, 0), Vector2.from_xy(10, 20))
    assert type(rect.proto) is base_types_pb2.GraphicShape
    assert rect.proto.WhichOneof("geometry") == "rectangle"

    poly = Polygon.from_outline(PolyLine())
    assert type(poly.proto) is base_types_pb2.GraphicShape
    assert poly.proto.WhichOneof("geometry") == "polygon"

    assert type(GraphicShape(rect.proto).proto) is base_types_pb2.GraphicShape


def test_schematic_graphic_shape_wire_round_trip():
    """SchematicGraphicShape embeds the inner GraphicShape; the full wrapper must
    still serialize as SchematicGraphicShape and the shape survive the trip."""
    from kipy.common_types import Rectangle, to_concrete_shape
    from kipy.schematic_types import SchematicGraphicShape, unwrap
    from kipy.util import pack_any

    sgs = SchematicGraphicShape()
    sgs.shape = Rectangle.from_coords(Vector2.from_xy(1000, 0), Vector2.from_xy(2000, 3000))

    packed = pack_any(sgs.proto)
    assert packed.type_url == "type.googleapis.com/kiapi.schematic.types.SchematicGraphicShape"

    restored = unwrap(packed)
    assert type(restored) is SchematicGraphicShape
    shape = to_concrete_shape(restored.shape)
    assert type(shape) is Rectangle
    assert shape.top_left == Vector2.from_xy(1000, 0)
    assert shape.bottom_right == Vector2.from_xy(2000, 3000)


def test_polygon_with_holes_auto_close():
    """Default PolygonWithHoles force-closes assigned outlines; auto_close=False
    preserves the polyline's own closed flag."""
    from kipy.geometry import PolygonWithHoles

    open_line = PolyLine()
    open_line.append(PolyLineNode.from_xy(0, 0))
    open_line.append(PolyLineNode.from_xy(1000, 0))

    default = PolygonWithHoles()
    default.outline = open_line
    assert default.outline.closed

    preserve = PolygonWithHoles(auto_close=False)
    preserve.outline = open_line
    assert not preserve.outline.closed
    assert len(preserve.outline.nodes) == 2


def test_zone_outline_forces_closed():
    """Zones require closed outlines regardless of the source polygon's auto_close
    flag; KiCad builds the SHAPE_POLY_SET directly without auto-closing."""
    from kipy.board_types import Zone
    from kipy.geometry import PolygonWithHoles

    open_line = PolyLine()
    open_line.append(PolyLineNode.from_xy(0, 0))
    open_line.append(PolyLineNode.from_xy(1000, 0))
    open_line.append(PolyLineNode.from_xy(1000, 1000))

    zone_poly = PolygonWithHoles(auto_close=False)
    zone_poly.outline = open_line
    hole = PolyLine()
    hole.append(PolyLineNode.from_xy(100, 100))
    hole.append(PolyLineNode.from_xy(200, 100))
    zone_poly.add_hole(hole)

    zone = Zone()
    zone.outline = zone_poly

    assert zone.outline.outline.closed
    assert all(h.closed for h in zone.outline.holes)


def test_schematic_rule_area_shape_forces_closed():
    """Rule areas must be closed polygons (KiCad's parser enforces this); the setter
    closes polygon outlines regardless of auto_close, and rejects non-polygons."""
    from kipy.common_types import Polygon, Rectangle
    from kipy.schematic_types import SchematicRuleArea

    open_line = PolyLine()
    open_line.append(PolyLineNode.from_xy(0, 0))
    open_line.append(PolyLineNode.from_xy(1000, 0))
    open_line.append(PolyLineNode.from_xy(1000, 1000))

    rule = SchematicRuleArea()
    rule.shape = Polygon.from_outline(open_line)
    assert rule.shape.polygons[0].outline.closed

    with pytest.raises(ValueError):
        rule.shape = Rectangle.from_coords(Vector2.from_xy(0, 0), Vector2.from_xy(1, 1))
