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

"""Live tests for geometry properties and moving/rotating board items.

These tests talk to a real, headless KiCad started via ``kicad-cli api-server``.
They are skipped unless ``pytest --live`` is passed and a ``kicad-cli`` binary is
available (via the ``KICAD_CLI`` environment variable, a repo-root ``.env`` file,
or the default install locations).  See ``tests/conftest.py``.
"""

import pytest

from kipy.board_types import BoardLayer, FootprintInstance, Pad, Track
from kipy.geometry import Angle, Vector2
from kipy.util.units import from_mm

pytestmark = pytest.mark.live


def _make_footprint(reference: str, pad_offset_mm: tuple[float, float]) -> FootprintInstance:
    footprint = FootprintInstance()
    footprint.layer = BoardLayer.BL_F_Cu
    footprint.reference_field.text.value = reference
    pad = Pad()
    pad.position = Vector2.from_xy_mm(*pad_offset_mm)
    footprint.definition.add_item(pad)
    return footprint


def _fetch_footprint(board, footprint: FootprintInstance) -> FootprintInstance:
    """Re-fetches a footprint from the board, proving the round trip to KiCad."""
    fetched = [fp for fp in board.get_footprints() if fp.id == footprint.id]
    assert len(fetched) == 1
    return fetched[0]


def _fetch_track(board, track: Track) -> Track:
    fetched = [t for t in board.get_tracks() if t.id == track.id]
    assert len(fetched) == 1
    return fetched[0]


def test_footprint_position_view_is_mutable(board):
    """The position property returns a live view of the item's proto: mutating it
    in place must be visible locally and persist through update_items."""
    created = board.create_items(_make_footprint("R1", (1, 0)))[0]
    assert created.position == Vector2.from_xy(0, 0)

    created.position.x = from_mm(20)
    created.position.y = from_mm(30)
    assert created.position == Vector2.from_xy_mm(20, 30)

    board.update_items([created])
    fetched = _fetch_footprint(board, created)
    assert fetched.position == Vector2.from_xy_mm(20, 30)


def test_footprint_position_view_supports_iadd(board):
    """+= on the position view mutates the underlying proto in place."""
    created = board.create_items(_make_footprint("R1", (1, 0)))[0]
    created.position += Vector2.from_xy_mm(5, 0)

    board.update_items([created])
    fetched = _fetch_footprint(board, created)
    assert fetched.position == Vector2.from_xy_mm(5, 0)


def test_footprint_position_setter_moves_children(board):
    """Assigning a new position moves pads and fields along with the footprint."""
    created = board.create_items(_make_footprint("R1", (1, 0)))[0]
    created.position = Vector2.from_xy_mm(10, 10)
    board.update_items([created])

    fetched = _fetch_footprint(board, created)
    assert fetched.position == Vector2.from_xy_mm(10, 10)
    assert fetched.definition.pads[0].position == Vector2.from_xy_mm(11, 10)
    assert fetched.reference_field.text.position == Vector2.from_xy_mm(10, 10)


def test_footprint_orientation_view_is_mutable(board):
    """The orientation property returns a live view: mutating it in place must be
    visible locally and persist through update_items."""
    created = board.create_items(_make_footprint("R1", (1, 0)))[0]
    assert created.orientation.degrees == 0

    created.orientation.degrees = 45
    assert created.orientation.degrees == pytest.approx(45)

    board.update_items([created])
    fetched = _fetch_footprint(board, created)
    assert fetched.orientation.degrees == pytest.approx(45)


def test_footprint_orientation_setter_rotates_children(board):
    """Assigning a new orientation rotates pads about the footprint origin.

    KiCad's y axis points down on screen, so a +90 degree rotation maps (2, 0)
    to (0, -2).
    """
    created = board.create_items(_make_footprint("R1", (2, 0)))[0]
    created.orientation = Angle.from_degrees(90)
    board.update_items([created])

    fetched = _fetch_footprint(board, created)
    assert fetched.orientation.degrees == pytest.approx(90)
    assert fetched.definition.pads[0].position == Vector2.from_xy_mm(0, -2)


def test_footprint_orientation_setter_normalizes_and_rotates(board):
    """The setter normalizes to [-180, 180) and rotates children by the delta.

    450 degrees is equivalent to 90; the stored orientation must normalize and
    the children must end up where a plain 90-degree rotation puts them.
    """
    created = board.create_items(_make_footprint("R1", (2, 0)))[0]
    created.orientation = Angle.from_degrees(450)
    board.update_items([created])

    fetched = _fetch_footprint(board, created)
    assert fetched.orientation.degrees == pytest.approx(90)
    assert fetched.definition.pads[0].position == Vector2.from_xy_mm(0, -2)


def test_footprint_orientation_setter_does_not_mutate_argument(board):
    """The setter must not normalize the caller's Angle object in place."""
    created = board.create_items(_make_footprint("R1", (1, 0)))[0]
    angle = Angle.from_degrees(370)
    created.orientation = angle
    assert angle.degrees == pytest.approx(370)


def test_footprint_rotation_round_trip_matches_expected_positions(board):
    """A footprint rotated through 0/90/180/270 degrees keeps its pad on the
    expected point of the circle around the footprint origin.

    Angles are stored normalized to [-180, 180), so 270 comes back as -90.
    """
    created = board.create_items(_make_footprint("R1", (2, 0)))[0]
    # (set degrees, expected pad position, expected stored degrees)
    expected = [
        (0, Vector2.from_xy_mm(2, 0), 0),
        (90, Vector2.from_xy_mm(0, -2), 90),
        (180, Vector2.from_xy_mm(-2, 0), 180),
        (270, Vector2.from_xy_mm(0, 2), -90),
    ]

    for degrees, pad_pos, stored in expected:
        created.orientation = Angle.from_degrees(degrees)
        board.update_items([created])
        fetched = _fetch_footprint(board, created)
        assert fetched.orientation.degrees == pytest.approx(stored)
        assert fetched.definition.pads[0].position == pad_pos


def test_pad_angle_view_is_mutable_and_persists(board):
    """PadStack.angle returns a live view; mutating it persists through
    update_items."""
    created = board.create_items(_make_footprint("R1", (1, 0)))[0]
    fetched = _fetch_footprint(board, created)

    pad = fetched.definition.pads[0]
    pad.padstack.angle.degrees = 30
    board.update_items([fetched])

    refetched = _fetch_footprint(board, created)
    assert refetched.definition.pads[0].padstack.angle.degrees == pytest.approx(30)


def test_track_start_view_is_mutable_and_persists(board):
    """Track start/end are live views; += moves the endpoint and persists."""
    track = Track()
    track.layer = BoardLayer.BL_F_Cu
    track.start = Vector2.from_xy_mm(10, 10)
    track.end = Vector2.from_xy_mm(30, 10)
    track.width = from_mm(0.2)
    created = board.create_items(track)[0]

    fetched = _fetch_track(board, created)
    fetched.start += Vector2.from_xy_mm(1, 0)
    board.update_items([fetched])

    refetched = _fetch_track(board, created)
    assert refetched.start == Vector2.from_xy_mm(11, 10)
    assert refetched.end == Vector2.from_xy_mm(30, 10)


def test_track_rotate_via_geometry_helper(board):
    """Rotating both endpoints of a track with Vector2.rotate lands them where
    KiCad's own rotation would."""
    track = Track()
    track.layer = BoardLayer.BL_F_Cu
    track.start = Vector2.from_xy_mm(10, 10)
    track.end = Vector2.from_xy_mm(20, 10)
    track.width = from_mm(0.2)
    created = board.create_items(track)[0]

    fetched = _fetch_track(board, created)
    center = Vector2.from_xy_mm(10, 10)
    angle = Angle.from_degrees(90)
    fetched.start = fetched.start.rotate(angle, center)
    fetched.end = fetched.end.rotate(angle, center)
    board.update_items([fetched])

    refetched = _fetch_track(board, created)
    assert refetched.start == Vector2.from_xy_mm(10, 10)
    assert refetched.end == Vector2.from_xy_mm(10, 0)
