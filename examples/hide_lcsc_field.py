#!/usr/bin/env python3
"""Hide the LCSC field on all footprints in the open PCBnew board."""

from kipy import KiCad
from kipy.board_types import Field

board = KiCad().get_board()
footprints = board.get_footprints()

changed = []
for footprint in footprints:
    for item in footprint.texts_and_fields:
        if isinstance(item, Field) and item.name == "LCSC":
            item.visible = False
            changed.append(footprint)
            break

board.update_items(changed)
print(f"Hid LCSC field on {len(changed)} footprint(s).")
