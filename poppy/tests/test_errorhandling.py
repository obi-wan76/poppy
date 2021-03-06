# This file contains code for testing various error handlers and user interface edge cases,
# as opposed to testing the main body of functionality of the code.

from .. import poppy_core
from .. import optics
from .. import matrixDFT
from .. import zernike
import sys
if sys.version_info.major < 3:
    _PYTHON_2 = True
else:
    _PYTHON_2 = False

try:
    import pytest
    _HAVE_PYTEST = True
except:
    _HAVE_PYTEST = False

def _exception_message_starts_with(excinfo, message_body):
    if _PYTHON_2:
        return excinfo.value.message.startswith(message_body)
    else:
        return excinfo.value.args[0].startswith(message_body)

if _HAVE_PYTEST:
    def test_calc_psf_catch_invalid_wavelength():
        """ Test that it rejects incompatible wavelengths"""

        osys = poppy_core.OpticalSystem("test")
        pupil = optics.CircularAperture(radius=1)
        osys.add_pupil(pupil) #function='Circle', radius=1)
        osys.add_detector(pixelscale=0.1, fov_arcsec=5.0) # use a large FOV so we grab essentially all the light and conserve flu

        with pytest.raises(ValueError) as excinfo:
            psf = osys.calc_psf('cat')
        assert _exception_message_starts_with(excinfo, "Argument 'wavelength' to function 'calc_psf' must be a number")


        source={'wavelengths': [1.0e-6, 'not a number', 1.2e-6, 1.3e-6], 'weights':[0.25, 0.25, 0.25, 0.25]}
        with pytest.raises(ValueError) as excinfo:
            psf = osys.calc_psf(source)
        assert _exception_message_starts_with(excinfo, "Argument 'wavelength' to function 'calc_psf' must be a number")

    def test_matrixDFT_catch_invalid_parameters():
        import numpy as np

        # invalid nlamD
        plane = np.zeros( (100,100))
        with pytest.raises(ValueError) as excinfo:
            matrixDFT.matrix_dft(plane, 'not allowed', 100)   # wrong type
        assert _exception_message_starts_with(excinfo, "'nlamD' must be supplied as a scalar (for square arrays) or as ")
        with pytest.raises(ValueError) as excinfo:
            matrixDFT.matrix_dft(plane, (1, 2, 3), 100)       # wrong dimensionality
        assert _exception_message_starts_with(excinfo, "'nlamD' must be supplied as a scalar (for square arrays) or as ")

        # invalid npix
        with pytest.raises(ValueError) as excinfo:
            matrixDFT.matrix_dft(plane, 10, "invalid")       # wrong type
        assert _exception_message_starts_with(excinfo, "'npix' must be supplied as a scalar (for square arrays) or as ")
        with pytest.raises(ValueError) as excinfo:
            matrixDFT.matrix_dft(plane, 10, (4,5,6))         # wrong dimensionality
        assert _exception_message_starts_with(excinfo, "'npix' must be supplied as a scalar (for square arrays) or as ")
        with pytest.raises(TypeError) as excinfo:
            matrixDFT.matrix_dft(plane, 10, 3.1415)          # must be an integer
        assert _exception_message_starts_with(excinfo, "'npix' must be supplied as integer value(s)")


        #invalid offset
        with pytest.raises(ValueError) as excinfo:
            matrixDFT.matrix_dft(plane, 10, 50, offset=(1,2,3), centering='adjustable')
        assert _exception_message_starts_with(excinfo, "'offset' must be supplied as a 2-tuple with")


        # invalid centering
        with pytest.raises(ValueError) as excinfo:
            matrixDFT.matrix_dft(plane, 10, 50, centering='Diagonal')
        assert _exception_message_starts_with(excinfo, "Invalid centering style")


    def test_inverseTransmission_invalid_parameters():
        import numpy as np
        with pytest.raises(ValueError) as excinfo:
            optics.InverseTransmission()
        assert _exception_message_starts_with(excinfo, "Need to supply an valid optic to invert!")

        with pytest.raises(ValueError) as excinfo:
            optics.InverseTransmission(optic=np.ones((100,100)))
        assert _exception_message_starts_with(excinfo, "Need to supply an valid optic to invert!")





    def test_CircularAperture_invalid_parameters():
        with pytest.raises(ValueError) as excinfo:
            optics.CircularAperture(radius='a')
        assert _exception_message_starts_with(excinfo, "Argument 'radius' to function '__init__' must be a number")


    def test_zernike_indices():
        with pytest.raises(ValueError) as excinfo:
            zernike.noll_indices(0)
        assert _exception_message_starts_with(excinfo, "Zernike index j must be a positive integer")


        with pytest.raises(ValueError) as excinfo:
            zernike.zernike(2,4)
        assert _exception_message_starts_with(excinfo, "Zernike index m must be >= index n")

