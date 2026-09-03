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

from kipy import KiCad
from kipy.common_types import PageOrientation, PageSize
from kipy.geometry import Vector2
from kipy.schematic_types import (
    SchematicLabelShape,
    SchematicLabelSpinStyle,
    SheetPin,
    SheetSymbol,
)

if __name__ == "__main__":
    kicad = KiCad()
    sch = kicad.get_schematic()

    settings = sch.get_page_settings()
    settings.page_size = PageSize.PS_ANSI_C
    settings.orientation = PageOrientation.PO_PORTRAIT
    sch.set_page_settings(settings)

    hierarchy = sch.get_hierarchy()

    subsheet = SheetSymbol()
    subsheet.name_field.visible = True
    subsheet.name_field.text.value = "Generated Sheet"
    subsheet.filename_field.visible = True
    subsheet.filename_field.text.value = "newsheet.kicad_sch"
    subsheet.position = Vector2.from_xy_mils(5000, 3000)
    subsheet.size = Vector2.from_xy_mils(1000, 750)

    pin1 = SheetPin()
    pin1.text.value = "DATA_IN"
    pin1.position = Vector2.from_xy_mils(5000, 3100)
    pin1.spin_style = SchematicLabelSpinStyle.SLSS_RIGHT
    pin1.shape = SchematicLabelShape.SLSH_INPUT

    pin2 = SheetPin()
    pin2.text.value = "DATA_OUT"
    pin2.position = Vector2.from_xy_mils(6000, 3100)
    pin2.shape = SchematicLabelShape.SLSH_OUTPUT

    subsheet.pins = [pin1, pin2]

    sch.create_items(subsheet)
