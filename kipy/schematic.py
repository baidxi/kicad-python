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
    DirectiveLabel,
    GlobalLabel,
    Group,
    HierarchicalLabel,
    Junction,
    LocalLabel,
    NoConnectMarker,
    SchematicGraphicShape,
    SchematicHierarchy,
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

    def _spec(self, sheet_path: SheetPath | SheetInstance | None) -> DocumentSpecifier:
        """Builds the document specifier for an item query.  When no sheet path is
        given, the specifier has no sheet path set, which requests items from all
        sheets in the document."""
        spec = DocumentSpecifier()
        spec.type = DocumentType.DOCTYPE_SCHEMATIC
        spec.project.CopyFrom(self._doc.project)
        if isinstance(sheet_path, SheetInstance):
            spec.sheet_path.CopyFrom(sheet_path.path.proto)
        elif isinstance(sheet_path, SheetPath):
            spec.sheet_path.CopyFrom(sheet_path.proto)
        elif sheet_path is not None:
            spec.sheet_path.CopyFrom(sheet_path)
        return spec

    def get_items(
        self,
        types: KiCadObjectType.ValueType | Sequence[KiCadObjectType.ValueType] | None = None,
        sheet_path: SheetPath | SheetInstance | None = None,
    ) -> Sequence[SchematicItem]:
        """Retrieves items from the schematic, optionally filtered to a single or set of
        types and/or to a single sheet.

        :param types: Optional type or types of items to retrieve.
        :param sheet_path: Optional sheet to scope the query to.  If not provided, items
            from all sheets in the schematic are returned.
        """
        return self._get_items(types, self._spec(sheet_path))

    def iter_sheets(self):
        """Iterates over all sheets in the schematic's hierarchy, depth-first, beginning
        with the root sheet."""
        yield from self.get_hierarchy()

    def get_lines(
        self, sheet_path: SheetPath | SheetInstance | None = None
    ) -> Sequence[SchematicLine]:
        return [
            cast(SchematicLine, item)
            for item in self.get_items(types=[KiCadObjectType.KOT_SCH_LINE], sheet_path=sheet_path)
        ]

    def get_text(
        self, sheet_path: SheetPath | SheetInstance | None = None
    ) -> Sequence[SchematicText | SchematicTextBox]:
        return [
            cast(SchematicText, item)
            if isinstance(item, SchematicText)
            else cast(SchematicTextBox, item)
            for item in self.get_items(
                types=[KiCadObjectType.KOT_SCH_TEXT, KiCadObjectType.KOT_SCH_TEXTBOX],
                sheet_path=sheet_path,
            )
        ]

    def get_shapes(
        self, sheet_path: SheetPath | SheetInstance | None = None
    ) -> Sequence[SchematicGraphicShape]:
        return [
            cast(SchematicGraphicShape, item)
            for item in self.get_items(
                types=[KiCadObjectType.KOT_SCH_SHAPE], sheet_path=sheet_path
            )
        ]

    def get_images(
        self, sheet_path: SheetPath | SheetInstance | None = None
    ) -> Sequence[SchematicImage]:
        return [
            cast(SchematicImage, item)
            for item in self.get_items(
                types=[KiCadObjectType.KOT_SCH_BITMAP], sheet_path=sheet_path
            )
        ]

    def get_labels(
        self, sheet_path: SheetPath | SheetInstance | None = None
    ) -> Sequence[LocalLabel | GlobalLabel | HierarchicalLabel | DirectiveLabel]:
        return [
            cast("LocalLabel | GlobalLabel | HierarchicalLabel | DirectiveLabel", item)
            for item in self.get_items(
                types=[
                    KiCadObjectType.KOT_SCH_LABEL,
                    KiCadObjectType.KOT_SCH_GLOBAL_LABEL,
                    KiCadObjectType.KOT_SCH_HIER_LABEL,
                    KiCadObjectType.KOT_SCH_DIRECTIVE_LABEL,
                ],
                sheet_path=sheet_path,
            )
        ]

    def get_symbols(
        self, sheet_path: SheetPath | SheetInstance | None = None
    ) -> Sequence[SchematicSymbolInstance]:
        return [
            cast(SchematicSymbolInstance, item)
            for item in self.get_items(
                types=[KiCadObjectType.KOT_SCH_SYMBOL], sheet_path=sheet_path
            )
        ]

    def get_sheet_symbols(
        self, sheet_path: SheetPath | SheetInstance | None = None
    ) -> Sequence[SheetSymbol]:
        return [
            cast(SheetSymbol, item)
            for item in self.get_items(
                types=[KiCadObjectType.KOT_SCH_SHEET], sheet_path=sheet_path
            )
        ]

    def get_junctions(
        self, sheet_path: SheetPath | SheetInstance | None = None
    ) -> Sequence[Junction]:
        """Returns all junctions in the schematic"""
        return [
            cast(Junction, item)
            for item in self.get_items(
                types=[KiCadObjectType.KOT_SCH_JUNCTION], sheet_path=sheet_path
            )
        ]

    def get_no_connects(
        self, sheet_path: SheetPath | SheetInstance | None = None
    ) -> Sequence[NoConnectMarker]:
        """Returns all no-connect markers in the schematic"""
        return [
            cast(NoConnectMarker, item)
            for item in self.get_items(
                types=[KiCadObjectType.KOT_SCH_NO_CONNECT], sheet_path=sheet_path
            )
        ]

    def get_bus_entries(
        self, sheet_path: SheetPath | SheetInstance | None = None
    ) -> Sequence[BusEntry]:
        """Returns all wire-to-bus and bus-to-bus entries in the schematic"""
        return [
            cast(BusEntry, item)
            for item in self.get_items(
                types=[
                    KiCadObjectType.KOT_SCH_BUS_WIRE_ENTRY,
                    KiCadObjectType.KOT_SCH_BUS_BUS_ENTRY,
                ],
                sheet_path=sheet_path,
            )
        ]

    def get_rule_areas(
        self, sheet_path: SheetPath | SheetInstance | None = None
    ) -> Sequence[SchematicRuleArea]:
        """Returns all rule areas (schematic keepouts) in the schematic"""
        return [
            cast(SchematicRuleArea, item)
            for item in self.get_items(
                types=[KiCadObjectType.KOT_SCH_RULE_AREA], sheet_path=sheet_path
            )
        ]

    def get_tables(
        self, sheet_path: SheetPath | SheetInstance | None = None
    ) -> Sequence[SchematicTable]:
        return [
            cast(SchematicTable, item)
            for item in self.get_items(
                types=[KiCadObjectType.KOT_SCH_TABLE], sheet_path=sheet_path
            )
        ]

    def get_groups(self, sheet_path: SheetPath | SheetInstance | None = None) -> Sequence[Group]:
        return [
            cast(Group, item)
            for item in self.get_items(
                types=[KiCadObjectType.KOT_SCH_GROUP], sheet_path=sheet_path
            )
        ]

    def get_hierarchy(self) -> SchematicHierarchy:
        """Retrieves the sheet hierarchy of the schematic.

        The returned object provides access to the root sheet (``root``), and can
        be iterated directly to walk every sheet in the hierarchy depth-first.
        """
        command = GetSchematicHierarchy()
        command.document.CopyFrom(self._doc)
        response = self._kicad.send(command, SchematicHierarchyResponse)
        return SchematicHierarchy(
            [SheetInstance(proto=sheet) for sheet in response.top_level_sheets]
        )

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
