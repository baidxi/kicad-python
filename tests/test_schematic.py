from typing import Type

import pytest

from kipy.proto.common.types import DocumentSpecifier, DocumentType, jobs_pb2
from kipy.proto.schematic import schematic_jobs_pb2
from kipy.schematic import Schematic
from kipy.schematic_jobs import PlotSettings


class FakeClient:
    def __init__(self):
        self.command = None
        self.response_type = None

    def send(self, command, response_type):
        self.command = command
        self.response_type = response_type
        response = jobs_pb2.RunJobResponse()
        response.status = jobs_pb2.JS_SUCCESS
        response.output_path.append("C:/exports/out")
        return response


def make_document() -> DocumentSpecifier:
    document = DocumentSpecifier()
    document.type = DocumentType.DOCTYPE_SCHEMATIC
    document.project.name = "demo"
    return document


def make_plot_settings() -> PlotSettings:
    plot_settings = PlotSettings()
    plot_settings.drawing_sheet = "A4"
    plot_settings.default_font = "KiCad Font"
    plot_settings.variant = "Assembly"
    plot_settings.plot_all = True
    plot_settings.plot_drawing_sheet = True
    plot_settings.plot_pages = ["/", "/power"]
    plot_settings.show_hop_over = True
    plot_settings.black_and_white = True
    plot_settings.page_size = schematic_jobs_pb2.SJPS_A4
    plot_settings.use_background_color = True
    plot_settings.min_pen_width = 12
    plot_settings.theme = "Plot"
    return plot_settings


def test_schematic_plot_settings_wrap_proto_fields():
    plot_settings = make_plot_settings()

    assert plot_settings.drawing_sheet == "A4"
    assert plot_settings.default_font == "KiCad Font"
    assert plot_settings.variant == "Assembly"
    assert plot_settings.plot_all is True
    assert plot_settings.plot_drawing_sheet is True
    assert plot_settings.plot_pages == ["/", "/power"]
    assert plot_settings.show_hop_over is True
    assert plot_settings.black_and_white is True
    assert plot_settings.page_size == schematic_jobs_pb2.SJPS_A4
    assert plot_settings.use_background_color is True
    assert plot_settings.min_pen_width == 12
    assert plot_settings.theme == "Plot"


@pytest.mark.parametrize(
    ("method_name", "command_type"),
    [
        ("export_svg", schematic_jobs_pb2.RunSchematicJobExportSvg),
        ("export_dxf", schematic_jobs_pb2.RunSchematicJobExportDxf),
        ("export_ps", schematic_jobs_pb2.RunSchematicJobExportPs),
    ],
)
def test_schematic_plot_exports_send_expected_job_request(
    method_name: str,
    command_type: Type,
):
    client = FakeClient()
    document = make_document()
    schematic = Schematic(client, document)
    plot_settings = make_plot_settings()

    result = getattr(schematic, method_name)(
        "C:/exports/out",
        plot_settings=plot_settings,
    )

    assert result.succeeded is True
    assert isinstance(client.command, command_type)
    assert client.response_type is jobs_pb2.RunJobResponse
    assert client.command.job_settings.document == document
    assert client.command.job_settings.output_path == "C:/exports/out"
    assert client.command.plot_settings == plot_settings.proto


def test_schematic_export_pdf_sends_expected_job_request():
    client = FakeClient()
    document = make_document()
    schematic = Schematic(client, document)
    plot_settings = make_plot_settings()

    result = schematic.export_pdf(
        "C:/exports/out",
        plot_settings=plot_settings,
        property_popups=True,
        hierarchical_links=True,
        include_metadata=False,
    )

    assert result.succeeded is True
    assert isinstance(client.command, schematic_jobs_pb2.RunSchematicJobExportPdf)
    assert client.response_type is jobs_pb2.RunJobResponse
    assert client.command.job_settings.document == document
    assert client.command.job_settings.output_path == "C:/exports/out"
    assert client.command.plot_settings == plot_settings.proto
    assert client.command.property_popups is True
    assert client.command.hierarchical_links is True
    assert client.command.include_metadata is False


def test_schematic_plot_export_rejects_file_like_directory_target():
    client = FakeClient()
    document = make_document()
    schematic = Schematic(client, document)

    with pytest.raises(
        ValueError,
        match="output_dir must point to an output directory for schematic SVG export, not a .svg file path",
    ):
        schematic.export_svg("C:/exports/demo.svg")


def test_schematic_pdf_export_rejects_directory_like_file_target():
    client = FakeClient()
    document = make_document()
    schematic = Schematic(client, document)

    with pytest.raises(
        ValueError,
        match="output_file must point to an output file for schematic PDF export, not a directory path",
    ):
        schematic.export_pdf("C:/exports/pdf-output/")