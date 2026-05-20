Schematic
=========

.. note::

   Schematic export uses format-specific output targets.
   ``Schematic.export_svg()``, ``Schematic.export_dxf()``, and ``Schematic.export_ps()``
   take an ``output_dir`` because KiCad writes one file per plotted sheet into a
   directory. ``Schematic.export_pdf()`` takes an ``output_file`` because KiCad
   writes a single PDF file. ``Schematic.export_netlist()`` and
   ``Schematic.export_bom()`` also take an ``output_file``.

.. automodule:: kipy.schematic
   :members:
   :undoc-members:

Schematic Types
===============

.. automodule:: kipy.schematic_types
   :members:
   :undoc-members:

Schematic Jobs
==============

.. automodule:: kipy.schematic_jobs
   :members:
   :undoc-members:
