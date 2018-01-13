
from abc import ABCMeta
from functools import wraps
from types import FunctionType

from pyvisa import ResourceManager
from pyvisa.errors import VisaIOError
from pyvisa.resources import GPIBInstrument
from serial import Serial, SerialException
from serial.rs485 import RS485

from . import InstrumentException


def general_exception(func, *wrapped_exc):
    def new_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (VisaIOError, SerialException):
            raise InstrumentException
    return new_func

class MetaInstrument(ABCMeta):
    """
    Metaclass that wraps all methods so that VisaIOError and SerialException
    are raised as InstrumentException.
    """

    def __init__(self, clsname, bases, clsdict):
        super().__init__(clsname, bases, clsdict)

        for name, value in clsdict.items():
            if not isinstance(value, FunctionType): 
                continue
            else:
                setattr(self, name, general_exception(value))

class Singleton(ABCMeta):
    """ 
    Metaclass for singleton classes. Creating a new instance
    of a singleton class silently returns the existing instance. 
    """

    _instances = dict()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class GPIBBase(metaclass = MetaInstrument):
    """ 
    Base class for GPIB instruments. It wraps PyVisa's ResourceManager with open resources.
    ``GPIBBase`` also supports context managemenent (``with`` statement).
    
    Parameters
    ----------
    addr : str
        Instrument address, e.g. 'GPIB::15'.
    kwargs
        Keyword arguments are passed to the pyvisa.ResourceManager.open_resource method.
    """

    def __init__(self, addr, **kwargs):
        self._rm = ResourceManager()
        self._instrument = self._rm.open_resource(resource_name = addr, **kwargs)

    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        self._instrument.close()
        self._rm.close()

    def write(self, *args, **kwargs):
        return self._instrument.write(*args, **kwargs)
    
    def read(self, *args, **kwargs):
        return self._instrument.read(*args, **kwargs)
    
    def query(self, *args, **kwargs):
        return self._instrument.query(*args, **kwargs)

    write.__doc__ = GPIBInstrument.write.__doc__
    read.__doc__  = GPIBInstrument.read.__doc__
    query.__doc__ = GPIBInstrument.query.__doc__

    def wait_for_srq(self, timeout = 25000):
        """
        Wait for a serial request (SRQ) or the timeout to expire.

        Parameters
        ----------
        timeout : int or None, optional
            The maximum waiting time in milliseconds. 
            None means waiting forever if necessary.
        
        Raises
        ------
        pyvisa.error.VisaIOError: if timeout has expired
        """
        return self._instrument.wait_for_srq(timeout)

class SerialBase(Serial, metaclass = MetaInstrument):
    """
    Base class for serial instruments.
    """
    ENCODING = 'ascii'

    def read_str(self, *args, **kwargs):
        """
        Read strings from instrument. Strings are automatically
        decoded.

        Parameters
        ----------
        size : int
            Number of bytes to read. Bytes are decoded in according to the 
            instrument's ``ENCODING`` attribute.

        Returns
        -------
        data : str
            Read information. If the instrument timeout was exceeded,
            ``data`` will be an empty or incomplete string.
        """
        return super().read(*args, **kwargs).decode(self.ENCODING)

    def write_str(self, data, *args, **kwargs):
        """
        Write strings to instrument. Strings are automatically
        encoded.

        Parameters
        ----------
        data : str
            Data to be sent. Strings are encoded in according to the 
            instrument's ``ENCODING`` attribute.

        Returns
        -------
        sent : int
            Number of bytes successfully written.

        Raises
        ------
        InstrumentException : incomplete write
        """
        return super().write(data.encode(self.ENCODING), *args, **kwargs)

class RS485Base(RS485, metaclass = MetaInstrument):
    """
    Base class for RS485 instruments.
    """
    ENCODING = 'ascii'

    def read_str(self, *args, **kwargs):
        """
        Read strings from instrument. Strings are automatically
        decoded.

        Parameters
        ----------
        size : int
            Number of bytes to read. Bytes are decoded in according to the 
            instrument's ``ENCODING`` attribute.

        Returns
        -------
        data : str
            Read information. If the instrument timeout was exceeded,
            ``data`` will be an empty or incomplete string.
        """
        return super().read(*args, **kwargs).decode(self.ENCODING)

    def write_str(self, data, *args, **kwargs):
        """
        Write strings to instrument. Strings are automatically
        encoded.

        Parameters
        ----------
        data : str
            Data to be sent. Strings are encoded in according to the 
            instrument's ``ENCODING`` attribute.

        Returns
        -------
        sent : int
            Number of bytes successfully written.

        Raises
        ------
        InstrumentException : incomplete write
        """
        return super().write(data.encode(self.ENCODING), *args, **kwargs)
