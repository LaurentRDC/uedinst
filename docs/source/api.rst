

.. _api:

*************
Reference/API
*************

.. currentmodule:: uedinst

==================
Instrument Classes
==================

.. autoclass:: GatanUltrascan895
    :members:
    :show-inheritance:
    :member-order:

.. autoclass:: Merlin
    :members:
    :show-inheritance:
    :member-order:
    
.. autoclass:: SC10Shutter
    :members:
    :show-inheritance:
    :member-order:

.. autoclass:: PCI6281
    :members:
    :show-inheritance:
    :member-order:

.. autoclass:: Keithley6514
    :members:
    :show-inheritance:
    :member-order:

.. autoclass:: TekPSM4120
    :members:
    :show-inheritance:
    :member-order:

.. autoclass:: KLSeries979
    :members:
    :show-inheritance:
    :member-order:

.. autoclass:: HeinzingerPNChp
    :members:
    :show-inheritance:
    :member-order:

.. autoclass:: ILS250PP
    :members:
    :show-inheritance:
    :member-order:

.. autoclass:: RacalDana1991
    :members:
    :show-inheritance:
    :member-order:

.. autoclass:: ITC503
    :members:
    :show-inheritance:
    :member-order:

============
Base Classes
============

.. autoclass:: GPIBBase
    :members:
    :show-inheritance:
    :member-order:

.. autoclass:: SerialBase
    :members:
    :show-inheritance:
    :member-order:

.. autoclass:: RS485Base
    :members:
    :show-inheritance:
    :member-order:

.. autoclass:: MetaInstrument
    :members:
    :show-inheritance:
    :member-order:

=========
Exception
=========

Since some instruments can be controlled by either serial connections or GPIB, `uedinst` provides an abstraction
over both

.. autoexception:: InstrumentException

=========
Utilities
=========

.. autosummary::
    
    is_valid_IP
    timeout