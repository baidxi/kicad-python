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

from typing import cast, Sequence
from kipy import KiCad
from kipy.board_types import FootprintInstance, Pad
from kipy.proto.common.types import KIID, KiCadObjectType

b = KiCad().get_board()
all_nets = b.get_nets()

net_footprint_ids = []
footprint_ids: dict[str, KIID] = {}

for net in all_nets:
    pads = cast(Sequence[Pad], b.get_items_by_net(net, KiCadObjectType.KOT_PCB_PAD))
    parent_ids = []
    for pad in pads:
        parent = pad.parent
        if parent is not None:
            parent_ids.append(parent.value)
            footprint_ids.setdefault(parent.value, parent)
    net_footprint_ids.append((net, parent_ids))

# Fetch only the footprints we need (saves time on boards with many footprints)
fetched = b.get_items_by_id(list(footprint_ids.values()))
footprints = {fp.id.value: fp for fp in fetched if isinstance(fp, FootprintInstance)}

for net, parent_ids in net_footprint_ids:
    connected = [footprints[fpid] for fpid in parent_ids if fpid in footprints]

    # Example: identify testpoints as anything with a reference containing 'TP';
    # modify this criteria if you want to filter by something else
    testpoints = [fp for fp in connected if "TP" in fp.reference_field.text.value]

    if len(connected) > 1:
        if not testpoints:
            print(f"Net {net.name} has no testpoints")
        else:
            print(f"Net {net.name} has testpoints: {[tp.reference_field.text.value for tp in testpoints]}")
