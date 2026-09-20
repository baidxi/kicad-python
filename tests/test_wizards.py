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

"""Tests for the wizard protocol harness in kipy.wizards"""

from __future__ import annotations

import argparse
import json

import pytest
from google.protobuf.json_format import MessageToJson

from kipy.proto.common import types
from kipy.util.units import from_mm
from kipy.wizards import WizardBase, WizardParameter


def _params_json(params: list[WizardParameter]) -> str:
    container = types.WizardParameterList()
    for param in params:
        container.parameters.append(param.proto)
    return MessageToJson(container, preserving_proto_field_name=True)


class _MinimalWizard(WizardBase):
    def __init__(self):
        super().__init__(description="test wizard")


def _args(params: str | None) -> argparse.Namespace:
    return argparse.Namespace(get_info=False, generate=True, params=params, lang="en")


def test_parses_snake_case_params():
    params = [
        WizardParameter.create(
            "e",
            "Pad Pitch",
            types.WizardParameterCategory.WPC_PADS,
            types.WizardParameterDataType.WPDT_DISTANCE,
            from_mm(0.8),
        )
    ]

    loaded, error = _MinimalWizard()._load_generate_parameters(_args(_params_json(params)))

    assert error is None
    assert loaded is not None
    assert len(loaded) == 1
    assert loaded[0].identifier == "e"
    assert loaded[0].value == from_mm(0.8)


def test_parses_camel_case_params():
    """KiCad serializes with default (camelCase) field names."""
    params_json = json.dumps(
        {
            "parameters": [
                {
                    "identifier": "e",
                    "name": "Pad Pitch",
                    "category": "WPC_PADS",
                    "type": "WPDT_DISTANCE",
                    "int": {"value": from_mm(0.8)},
                }
            ]
        }
    )

    loaded, error = _MinimalWizard()._load_generate_parameters(_args(params_json))

    assert error is None
    assert loaded is not None
    assert loaded[0].identifier == "e"
    assert loaded[0].value == from_mm(0.8)


def test_ignores_unknown_fields():
    """Future KiCad versions may add fields"""
    params_json = json.dumps(
        {
            "parameters": [
                {
                    "identifier": "e",
                    "name": "Pad Pitch",
                    "category": "WPC_PADS",
                    "type": "WPDT_DISTANCE",
                    "int": {"value": from_mm(0.8), "futureField": 42},
                    "someFutureParameterField": "whatever",
                }
            ]
        }
    )

    loaded, error = _MinimalWizard()._load_generate_parameters(_args(params_json))

    assert error is None
    assert loaded is not None
    assert loaded[0].value == from_mm(0.8)


def test_invalid_json_returns_error():
    loaded, error = _MinimalWizard()._load_generate_parameters(_args("{not json"))

    assert loaded is None
    assert error is not None
    assert "Invalid --params" in error


def test_wrong_value_type_returns_error():
    params_json = json.dumps({"parameters": [{"identifier": "e", "int": {"value": "oops"}}]})

    loaded, error = _MinimalWizard()._load_generate_parameters(_args(params_json))

    assert loaded is None
    assert error is not None
    assert "Invalid --params" in error


def test_none_params_returns_none():
    loaded, error = _MinimalWizard()._load_generate_parameters(_args(None))

    assert loaded is None
    assert error is None


def test_round_trip_preserves_all_scalar_types():
    params = [
        WizardParameter.create(
            "count",
            "Count",
            types.WizardParameterCategory.WPC_PADS,
            types.WizardParameterDataType.WPDT_INTEGER,
            6,
            min_value=1,
            max_value=10,
            multiple=2,
        ),
        WizardParameter.create(
            "angle",
            "Angle",
            types.WizardParameterCategory.WPC_PADS,
            types.WizardParameterDataType.WPDT_ANGLE,
            90.0,
        ),
        WizardParameter.create(
            "flag",
            "Flag",
            types.WizardParameterCategory.WPC_PADS,
            types.WizardParameterDataType.WPDT_BOOL,
            True,
        ),
        WizardParameter.create(
            "label",
            "Label",
            types.WizardParameterCategory.WPC_METADATA,
            types.WizardParameterDataType.WPDT_STRING,
            "abc",
            validation_regex="[a-z]+",
        ),
    ]

    loaded, error = _MinimalWizard()._load_generate_parameters(_args(_params_json(params)))

    assert error is None
    assert loaded is not None
    by_id = {param.identifier: param for param in loaded}
    assert by_id["count"].int_min == 1
    assert by_id["count"].int_max == 10
    assert by_id["count"].int_multiple == 2
    assert by_id["angle"].value == pytest.approx(90.0)
    assert by_id["flag"].value is True
    assert by_id["label"].value == "abc"
    assert by_id["label"].string_validation_regex == "[a-z]+"


def test_generation_value_error_surfaces_as_wgs_error():
    """Cross-field validation errors must reach KiCad as WGS_ERROR"""

    class _FailingWizard(WizardBase):
        def __init__(self):
            super().__init__(description="failing wizard")

        def build_generated_content(self, parameters=None):
            raise ValueError("Parameter 'n' must be >= 4 and a multiple of 4")

    wizard = _FailingWizard()
    generated = wizard._generate([])
    assert generated.status == types.WizardGenerationStatus.WGS_ERROR
    assert "multiple of 4" in generated.error_message


def test_real_parameter_defaults():
    param = WizardParameter.create(
        "x",
        "X",
        types.WizardParameterCategory.WPC_PADS,
        types.WizardParameterDataType.WPDT_REAL,
        2.5,
    )
    assert param.value == pytest.approx(2.5)
    assert param.default_value == pytest.approx(2.5)


def test_value_clearing():
    param = WizardParameter.create(
        "x",
        "X",
        types.WizardParameterCategory.WPC_PADS,
        types.WizardParameterDataType.WPDT_INTEGER,
        3,
    )
    param.value = None
    assert param.value is None
    assert param.which_value() is None


def test_which_value_covers_real():
    param = WizardParameter.create(
        "x",
        "X",
        types.WizardParameterCategory.WPC_PADS,
        types.WizardParameterDataType.WPDT_REAL,
        1.5,
    )
    assert param.which_value() == "real"


def test_wrapper_proto_isolation():
    """WizardParameter(proto=...) copies, proto_ref references in place."""
    source = WizardParameter.create(
        "x",
        "X",
        types.WizardParameterCategory.WPC_PADS,
        types.WizardParameterDataType.WPDT_INTEGER,
        3,
    )

    copied = WizardParameter(proto=source.proto)
    referenced = WizardParameter(proto_ref=source.proto)

    copied.value = 5
    assert source.value == 3

    referenced.value = 7
    assert source.value == 7
