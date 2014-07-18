from ...wcs import specwcs
import numpy as np
import pytest
import astropy
from astropy import constants
from astropy import units as u

version = astropy.__version__.split('.')
minversion = pytest.mark.skipif(version[0] == '0' and version[1] < '4',
                                reason="at least astropy-0.4 required")

def test_doppler():
    doppler_factor = 1.38
    wcs = specwcs.DopplerShift(doppler_factor)
    x = np.array([1.25, 4.3])
    y = x* doppler_factor
    np.testing.assert_allclose(y, wcs(x))

def test_doppler_velocity():
    velocity = 1.38 * u.meter / u.second
    wcs = specwcs.DopplerShift.from_velocity(velocity)
    x = np.array([1.25, 4.3])
    beta = velocity / constants.c
    doppler_factor = ((1 + beta)/(1-beta)) ** 0.5
    y = x * doppler_factor
    np.testing.assert_allclose(y, wcs(x))

def test_composite_wcs():
    doppler_wcs = specwcs.DopplerShift(1.38)
    log_wcs = lambda x: 10 ** x

    def add_one(x):
        return x + 1
    wcs = specwcs.CompositeWCS(wcs_list=[doppler_wcs, log_wcs, add_one])
    x = np.random.random(10)
    y = add_one(log_wcs(doppler_wcs(x)))
    np.testing.assert_allclose(y, wcs(x))

def test_weighted_wcs():
    doppler_wcs1 = specwcs.DopplerShift(1.38)
    doppler_wcs2 = specwcs.DopplerShift(0.45)
    weight1 = 1.2
    weight2 = 2
    zero_offset1 = 1

    wcs = specwcs.WeightedCombinationWCS()
    wcs.add_WCS(doppler_wcs1, weight1, zero_offset1)
    wcs.add_WCS(doppler_wcs2, weight2)

    x = np.random.random(10)
    y = weight1 * (zero_offset1 + doppler_wcs1(x)) + weight2 * (doppler_wcs2(x))
    np.testing.assert_allclose(y, wcs(x))
