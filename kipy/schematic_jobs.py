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

from typing import Optional, Sequence

from kipy.board_jobs import JobResult
from kipy.proto.schematic import schematic_jobs_pb2
from kipy.wrapper import Wrapper

__all__ = ("JobResult", "PlotSettings")


class PlotSettings(Wrapper):
    """Shared settings for schematic plotting jobs"""

    def __init__(
        self,
        proto: Optional[schematic_jobs_pb2.SchematicPlotSettings] = None,
        proto_ref: Optional[schematic_jobs_pb2.SchematicPlotSettings] = None,
    ):
        self._proto = (
            proto_ref
            if proto_ref is not None
            else schematic_jobs_pb2.SchematicPlotSettings()
        )
        if proto is not None:
            self._proto.CopyFrom(proto)

    @property
    def drawing_sheet(self) -> str:
        return self._proto.drawing_sheet

    @drawing_sheet.setter
    def drawing_sheet(self, value: str):
        self._proto.drawing_sheet = value

    @property
    def default_font(self) -> str:
        return self._proto.default_font

    @default_font.setter
    def default_font(self, value: str):
        self._proto.default_font = value

    @property
    def variant(self) -> str:
        return self._proto.variant

    @variant.setter
    def variant(self, value: str):
        self._proto.variant = value

    @property
    def plot_all(self) -> bool:
        return self._proto.plot_all

    @plot_all.setter
    def plot_all(self, value: bool):
        self._proto.plot_all = value

    @property
    def plot_drawing_sheet(self) -> bool:
        return self._proto.plot_drawing_sheet

    @plot_drawing_sheet.setter
    def plot_drawing_sheet(self, value: bool):
        self._proto.plot_drawing_sheet = value

    @property
    def plot_pages(self) -> list[str]:
        return list(self._proto.plot_pages)

    @plot_pages.setter
    def plot_pages(self, value: Sequence[str]):
        del self._proto.plot_pages[:]
        self._proto.plot_pages.extend(value)

    @property
    def show_hop_over(self) -> bool:
        return self._proto.show_hop_over

    @show_hop_over.setter
    def show_hop_over(self, value: bool):
        self._proto.show_hop_over = value

    @property
    def black_and_white(self) -> bool:
        return self._proto.black_and_white

    @black_and_white.setter
    def black_and_white(self, value: bool):
        self._proto.black_and_white = value

    @property
    def page_size(self) -> schematic_jobs_pb2.SchematicJobPageSize.ValueType:
        return self._proto.page_size

    @page_size.setter
    def page_size(self, value: schematic_jobs_pb2.SchematicJobPageSize.ValueType):
        self._proto.page_size = value

    @property
    def use_background_color(self) -> bool:
        return self._proto.use_background_color

    @use_background_color.setter
    def use_background_color(self, value: bool):
        self._proto.use_background_color = value

    @property
    def min_pen_width(self) -> int:
        return self._proto.min_pen_width

    @min_pen_width.setter
    def min_pen_width(self, value: int):
        self._proto.min_pen_width = value

    @property
    def theme(self) -> str:
        return self._proto.theme

    @theme.setter
    def theme(self, value: str):
        self._proto.theme = value