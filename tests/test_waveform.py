import numpy as np
import pytest
from waveform import UniversalWaveMode


def test_default_instantiation():
    """Test default instantiation of UniversalWaveMode."""
    mode = UniversalWaveMode()
    # Check that the waveform, phase, and amplitude are not None after instantiation
    assert mode.waveform is not None
    assert mode.phase is not None
    assert mode.amplitude is not None


def test_invalid_nu_raises():
    """Test that an invalid value for nu raises a ValueError."""
    with pytest.raises(ValueError):
        UniversalWaveMode(nu=0.3)  # nu should be between 0 and 0.25


def test_time_out_of_bounds_truncation():
    """Test that the time array is truncated if it exceeds the valid bounds."""
    long_time = np.arange(-1e5, 1e3, 10)
    mode = UniversalWaveMode(time_array=long_time, nu=1e-3)
    # Ensure that all time values are within the valid range
    assert all(mode.time_array <= 100.)
    assert all(mode.time_array >= -2.5e2 / 1e-3)
