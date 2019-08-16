from pathlib import Path
from tempfile import gettempdir
from time import sleep

import numpy as np

from . import InstrumentException, TCPBase

TEMPDIR = Path(gettempdir())
INT16INFO = np.iinfo(np.int16)


class GatanUltrascan895(TCPBase):
    """
    Interface to the Gatan Ultrascan 895 camera server.

    The IP address defaults to 127.0.0.1:42057.

    Parameters
    ----------
    addr : string, optional
        IP address of the uedinst server plugin
    port : int, optional
        IP port of the uedinst server plugin
    tempdir : path or None, optional
        Path to the temporary directory to use when saving pictures.
    """

    def __init__(self, addr="127.0.0.1", port=42057, tempdir=None, **kwargs):
        try:
            super().__init__(addr=addr, port=port, **kwargs)
        except InstrumentException:
            raise InstrumentException(
                "Could not connect to DigitalMicrograph. Make sure it is open."
            )

        # Check that it is possible to get the version
        #  The ealiest versions of the plugin did not support
        # this, so an error might be raised.
        try:
            self.version = self.send_command("ULTRASCAN;VERSION")
        except InstrumentException:
            raise InstrumentException(
                "The uedinst plugin version installed in the GMS is too old."
            )

        if tempdir is None:
            tempdir = gettempdir()
        self.tempdir = Path(tempdir)  # Path() is idempotent

    @property
    def temp_image_fname(self):
        """ Path to the temporary file where to save images """
        return self.tempdir / "_uedinst_temp.dat"

    def send_command(self, *commands, wait=0):
        """
        Send commands to the camera server. This method only returns
        once an answer has been received.
        
        Raises
        ------
        InstrumentException : if answer received indicates an error occurred.
        """
        total_command = "".join(commands)
        self.socket.send(total_command.encode("ascii"))
        if wait:
            sleep(wait)
        answer = self.socket.recv(10).decode(
            "ascii"
        )  # Since the answer is either "OK", "ERR", or a version string, 10 chars is enough

        if answer == "ERR":
            raise InstrumentException(
                f"Command failed: {total_command}.\nAnswer received: {answer}.\nSee the GMS result console for details."
            )

        return answer

    def insert(self, toggle):
        """
        Insert/uninsert into the beam.

        Parameters
        ----------
        toggle : bool
            If True, the camera will insert; otherwise, the camera will retract.

        Raises
        ------
        InstrumentException : if answer received indicates an error occurred.
        """
        toggle = str(toggle).upper()
        self.send_command("ULTRASCAN;INSERT;", toggle)

    def acquire_image(self, exposure, remove_dark=True, normalize_gain=True):
        """ 
        Acquire a gain-normalized image from the detector.
        
        Parameters
        ----------
        exposure : float
            Exposure [seconds].
        remove_dark : bool
            If True, the camera dark background will be subtracted by the
            Gatan Microscopy Suite.
        normalize_gain : bool
            If True, the image will be gain-normalized by the Gatan Microscopy Suite.
        
        Returns
        -------
        image : `~numpy.ndarray`, dtype int16

        Raises
        ------
        InstrumentException : if answer received indicates an error occurred.
        """
        # Use a temporary file so that there can never be any conflits
        # between subsequent acquisitions.
        # Note: we cannot use NamedTemporaryFile because it doesn't create
        # a name, but a file-like object.
        self.send_command(
            f"ULTRASCAN;ACQUIRE;{float(exposure):.3f},{str(remove_dark)},{str(normalize_gain)},{str(self.temp_image_fname)}",
            wait=exposure,
        )

        # We save the images as raw format
        # because the 'translation' to TIFF was buggy
        # Therefore, better to get to the raw data and cast ourselves.
        with open(self.temp_image_fname, mode="rb") as datafile:
            arr = np.fromfile(datafile, dtype=np.int32).reshape((2048, 2048))

        # Gatan Ultrascan 895 can't actually detect higher than ~30 000 counts
        # Therefore, we can safely cast as int16 (after clipping)
        np.clip(arr, INT16INFO.min, INT16INFO.max, out=arr)
        return arr.astype(np.int16)
