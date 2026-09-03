from kipy import KiCad
from kipy.geometry import Angle, Vector2

board = KiCad().get_board()
footprints = board.get_footprints()

for footprint in footprints:
    footprint.position += Vector2.from_xy_mm(5, 2)
    footprint.orientation += Angle.from_degrees(90)

board.update_items(footprints)
