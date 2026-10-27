"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ..common.types import base_types_pb2 as common_dot_types_dot_base__types__pb2
from ..common.types import enums_pb2 as common_dot_types_dot_enums__pb2
from ..schematic import schematic_types_pb2 as schematic_dot_schematic__types__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n"schematic/schematic_commands.proto\x12\x18kiapi.schematic.commands\x1a\x1dcommon/types/base_types.proto\x1a\x18common/types/enums.proto\x1a\x1fschematic/schematic_types.proto"P\n\x15GetSchematicHierarchy\x127\n\x08document\x18\x01 \x01(\x0b2%.kiapi.common.types.DocumentSpecifier"\x95\x01\n\x1aSchematicHierarchyResponse\x127\n\x08document\x18\x01 \x01(\x0b2%.kiapi.common.types.DocumentSpecifier\x12>\n\x10top_level_sheets\x18\x02 \x03(\x0b2$.kiapi.schematic.types.SheetInstance"\x82\x01\n\x13GetSchematicNetlist\x127\n\x08document\x18\x01 \x01(\x0b2%.kiapi.common.types.DocumentSpecifier\x122\n\x05types\x18\x02 \x03(\x0e2#.kiapi.common.types.KiCadObjectType"\x86\x01\n\x18SchematicNetlistResponse\x127\n\x08document\x18\x01 \x01(\x0b2%.kiapi.common.types.DocumentSpecifier\x121\n\x04nets\x18\x02 \x03(\x0b2#.kiapi.schematic.types.SchematicNet"\xa3\x03\n\x16PlaceSymbolFromLibrary\x12.\n\x06header\x18\x01 \x01(\x0b2\x1e.kiapi.common.types.ItemHeader\x125\n\x06lib_id\x18\x02 \x01(\x0b2%.kiapi.common.types.LibraryIdentifier\x12-\n\x08position\x18\x03 \x01(\x0b2\x1b.kiapi.common.types.Vector2\x12K\n\x0borientation\x18\x04 \x01(\x0e21.kiapi.schematic.types.SchematicSymbolOrientationH\x00\x88\x01\x01\x12=\n\x04unit\x18\x05 \x01(\x0b2*.kiapi.schematic.types.SchematicSymbolUnitH\x01\x88\x01\x01\x12\x16\n\treference\x18\x06 \x01(\tH\x02\x88\x01\x01\x12\x18\n\x0binteractive\x18\x07 \x01(\x08H\x03\x88\x01\x01B\x0e\n\x0c_orientationB\x07\n\x05_unitB\x0c\n\n_referenceB\x0e\n\x0c_interactiveb\x06proto3')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'schematic.schematic_commands_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _GETSCHEMATICHIERARCHY._serialized_start = 154
    _GETSCHEMATICHIERARCHY._serialized_end = 234
    _SCHEMATICHIERARCHYRESPONSE._serialized_start = 237
    _SCHEMATICHIERARCHYRESPONSE._serialized_end = 386
    _GETSCHEMATICNETLIST._serialized_start = 389
    _GETSCHEMATICNETLIST._serialized_end = 519
    _SCHEMATICNETLISTRESPONSE._serialized_start = 522
    _SCHEMATICNETLISTRESPONSE._serialized_end = 656
    _PLACESYMBOLFROMLIBRARY._serialized_start = 659
    _PLACESYMBOLFROMLIBRARY._serialized_end = 1078