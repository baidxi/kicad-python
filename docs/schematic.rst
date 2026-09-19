Schematic
=========

Schematics in KiCad can be composed of one or many different sheets, each with a unique sheet path
that identifies it.  The :py:class:`~kipy.schematic.Schematic` class can represent an entire
schematic or a view onto a single sheet.  Many of its methods can take an optional sheet path
parameter to filter to a particular path.

Schematics produce graphical outputs but also connectivity data (called a netlist).  KiCad uses
graphical position to establish connectivity: each connectable object (for example, a symbol pin,
wire segment, or label) has one or more connection points.  Each connection point is a position on
the graphical canvas, and items must exactly match in position to be considered connected.  For
this reason, it is standard to use a 50 mil (1.27mm) layout grid for placing all connected items in
a schematic.  The KiCad GUI has some safeguards to prevent accidentally placing items in a way that
they are close but not quite connected, but API clients need to do this themselves.

.. automodule:: kipy.schematic
   :members:
   :undoc-members:

Schematic Types
===============

These objects can be placed on a schematic (and some can also exist inside a schematic symbol).

.. automodule:: kipy.schematic_types
   :members:
   :undoc-members:

Schematic Jobs
===============

Classes related to schematic output jobs (file exports)

.. automodule:: kipy.schematic_jobs
   :members:
   :undoc-members:
