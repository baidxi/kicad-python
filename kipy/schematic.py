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

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast

from google.protobuf.empty_pb2 import Empty

from kipy.client import KiCadClient
from kipy.common_types import PageSettings, SheetPath, TitleBlockInfo
from kipy.editor import EditorCommandsHandler
from kipy.project import Project
from kipy.proto.common.commands import editor_commands_pb2
from kipy.proto.common.commands.editor_commands_pb2 import GetPageSettings, SetPageSettings
from kipy.proto.common.types import (
    DocumentSpecifier,
    DocumentType,
    KiCadObjectType,
    base_types_pb2,
)
from kipy.proto.schematic.schematic_commands_pb2 import (
    GetSchematicHierarchy,
    GetSchematicNetlist,
    SchematicHierarchyResponse,
    SchematicNetlistResponse,
)
from kipy.schematic_types import (
    BusEntry,
    Group,
    Junction,
    LocalLabel,
    NoConnectMarker,
    SchematicGraphicShape,
    SchematicImage,
    SchematicItem,
    SchematicLine,
    SchematicNet,
    SchematicRuleArea,
    SchematicSymbolInstance,
    SchematicTable,
    SchematicText,
    SchematicTextBox,
    SheetInstance,
    SheetSymbol,
    unwrap,
)
from kipy.variants import VariantsCommandHandler


class Schematic(EditorCommandsHandler["SchematicItem"], VariantsCommandHandler):
    """
    .. versionadded:: 0.x.y (KiCad 11)
    """

    def __init__(self, kicad: KiCadClient, document: DocumentSpecifier):
        self._kicad = kicad
        self._doc = document

    def __repr__(self) -> str:
        return f"Schematic(filename={self.name}, path={self._doc.sheet_path})"

    @property
    def client(self) -> KiCadClient:
        return self._kicad

    @property
    def document(self) -> DocumentSpecifier:
        return self._doc

    def get_project(self) -> Project:
        return Project(self._kicad, self._doc)

    @property
    def name(self) -> str:
        return self._doc.project.name + ".kicad_sch"

    def _item_from_message(self, message: Any) -> SchematicItem:
        """Converts an unwrapped protobuf message into a concrete schematic item wrapper"""
        item = cast(SchematicItem, unwrap(message))
        if isinstance(item, Group):
            item._item_resolver = self.get_items_by_id
        return item

    def get_lines(self) -> Sequence[SchematicLine]:
        return [
            cast(SchematicLine, item)
            for item in self.get_items(types=[KiCadObjectType.KOT_SCH_LINE])
        ]

    def get_text(self) -> Sequence[SchematicText | SchematicTextBox]:
        return [
            cast(SchematicText, item)
            if isinstance(item, SchematicText)
            else cast(SchematicTextBox, item)
            for item in self.get_items(
                types=[KiCadObjectType.KOT_SCH_TEXT, KiCadObjectType.KOT_SCH_TEXTBOX]
            )
        ]

    def get_shapes(self) -> Sequence[SchematicGraphicShape]:
        return [
            cast(SchematicGraphicShape, item)
            for item in self.get_items(types=[KiCadObjectType.KOT_SCH_SHAPE])
        ]

    def get_images(self) -> Sequence[SchematicImage]:
        return [
            cast(SchematicImage, item)
            for item in self.get_items(types=[KiCadObjectType.KOT_SCH_BITMAP])
        ]

    def get_labels(self) -> Sequence[LocalLabel]:
        return [
            cast(LocalLabel, item)
            for item in self.get_items(
                types=[
                    KiCadObjectType.KOT_SCH_LABEL,
                    KiCadObjectType.KOT_SCH_GLOBAL_LABEL,
                    KiCadObjectType.KOT_SCH_HIER_LABEL,
                    KiCadObjectType.KOT_SCH_DIRECTIVE_LABEL,
                ]
            )
        ]

    def get_symbols(self) -> Sequence[SchematicSymbolInstance]:
        return [
            cast(SchematicSymbolInstance, item)
            for item in self.get_items(types=[KiCadObjectType.KOT_SCH_SYMBOL])
        ]

    def get_sheet_symbols(self) -> Sequence[SheetSymbol]:
        return [
            cast(SheetSymbol, item)
            for item in self.get_items(types=[KiCadObjectType.KOT_SCH_SHEET])
        ]

    def get_junctions(self) -> Sequence[Junction]:
        """Returns all junctions in the schematic

        .. versionadded:: 0.9.0"""
        return [
            cast(Junction, item)
            for item in self.get_items(types=[KiCadObjectType.KOT_SCH_JUNCTION])
        ]

    def get_no_connects(self) -> Sequence[NoConnectMarker]:
        """Returns all no-connect markers in the schematic

        .. versionadded:: 0.9.0"""
        return [
            cast(NoConnectMarker, item)
            for item in self.get_items(types=[KiCadObjectType.KOT_SCH_NO_CONNECT])
        ]

    def get_bus_entries(self) -> Sequence[BusEntry]:
        """Returns all wire-to-bus and bus-to-bus entries in the schematic

        .. versionadded:: 0.9.0"""
        return [
            cast(BusEntry, item)
            for item in self.get_items(
                types=[
                    KiCadObjectType.KOT_SCH_BUS_WIRE_ENTRY,
                    KiCadObjectType.KOT_SCH_BUS_BUS_ENTRY,
                ]
            )
        ]

    def get_rule_areas(self) -> Sequence[SchematicRuleArea]:
        """Returns all rule areas (schematic keepouts) in the schematic

        .. versionadded:: 0.9.0"""
        return [
            cast(SchematicRuleArea, item)
            for item in self.get_items(types=[KiCadObjectType.KOT_SCH_RULE_AREA])
        ]

    def get_tables(self) -> Sequence[SchematicTable]:
        """Returns all tables in the schematic

        .. versionadded:: 0.9.0"""
        return [
            cast(SchematicTable, item)
            for item in self.get_items(types=[KiCadObjectType.KOT_SCH_TABLE])
        ]

    def get_groups(self) -> Sequence[Group]:
        return [
            cast(Group, item) for item in self.get_items(types=[KiCadObjectType.KOT_SCH_GROUP])
        ]

    def get_hierarchy(self) -> list[SheetInstance]:
        command = GetSchematicHierarchy()
        command.document.CopyFrom(self._doc)
        response = self._kicad.send(command, SchematicHierarchyResponse)
        return [SheetInstance(proto=sheet) for sheet in response.top_level_sheets]

    def for_sheet(self, sheet: SheetInstance | SheetPath) -> Schematic:
        """Returns a Schematic bound to the given sheet, e.g. one from :meth:`get_hierarchy` or
        one of its children.

        The returned object can be used to make calls (`get_items`, etc) on a subsheet.
        """
        spec = DocumentSpecifier()
        spec.type = DocumentType.DOCTYPE_SCHEMATIC
        spec.project.CopyFrom(self._doc.project)
        spec.sheet_path.CopyFrom(
            sheet.path.proto if isinstance(sheet, SheetInstance) else sheet.proto
        )
        return Schematic(self._kicad, spec)

    def get_netlist(
        self,
        types: KiCadObjectType.ValueType | Sequence[KiCadObjectType.ValueType] | None = None,
    ) -> list[SchematicNet]:
        command = GetSchematicNetlist()
        command.document.CopyFrom(self._doc)

        if types is not None:
            if isinstance(types, int):
                command.types.append(types)
            else:
                command.types.extend(types)

        response = self._kicad.send(command, SchematicNetlistResponse)
        return [SchematicNet(proto=net) for net in response.nets]

    def get_title_block(self) -> TitleBlockInfo:
        command = editor_commands_pb2.GetTitleBlockInfo()
        command.document.CopyFrom(self._doc)
        return TitleBlockInfo(self._kicad.send(command, base_types_pb2.TitleBlockInfo))

    def set_title_block(self, title_block: TitleBlockInfo):
        command = editor_commands_pb2.SetTitleBlockInfo()
        command.document.CopyFrom(self._doc)
        command.title_block.CopyFrom(title_block.proto)
        self._kicad.send(command, Empty)

    def get_page_settings(self) -> PageSettings:
        command = GetPageSettings()
        command.document.CopyFrom(self._doc)
        return PageSettings(self._kicad.send(command, base_types_pb2.PageSettings))

    def set_page_settings(self, page_settings: PageSettings) -> PageSettings:
        command = SetPageSettings()
        command.document.CopyFrom(self._doc)
        command.page_settings.CopyFrom(page_settings.proto)
        return PageSettings(self._kicad.send(command, base_types_pb2.PageSettings))
