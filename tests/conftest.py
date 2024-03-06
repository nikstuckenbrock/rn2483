"""This module contains general test configuration"""

import sys

import pytest

from tests import machine, utime_mock

# Mocks the micropython machine module
sys.modules["machine"] = machine

# Mocks the utime module
sys.modules["utime"] = utime_mock

from rn2483.rn2483 import RN2483  # noqa: E402


@pytest.fixture
def rn2483_instance():
    """Returns a working instance of the RN2483"""

    machine.MOCK_CONFIGURATION = machine.MockConfiguration.CORRECT_ANSWERS
    return RN2483(
        uart_id=0,
        tx_pin=12,
        rx_pin=13,
        reset_pin=10,
        app_eui="0123456789012345",
        app_key="01234567890123450123456789012345",
        debug=True,
        wdt=machine.WDT(),
    )
