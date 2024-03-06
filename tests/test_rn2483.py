"""This module tests the rn2483 library/class"""

import machine
import pytest

from rn2483.rn2483 import (
    RN2483,
    RN2483InvalidInput,
    RN2483InvalidResponse,
    RN2483NoResponseError,
)


def test_rn2483_construction_with_no_answer():
    """Test the RN2483 constructor with no answer from the microcontroller"""

    with pytest.raises(RN2483NoResponseError):
        RN2483(
            uart_id=0,
            tx_pin=12,
            rx_pin=13,
            reset_pin=10,
            app_eui="appeui",
            app_key="appkey",
            debug=False,
            wdt=machine.WDT(),
        )


def test_rn2483_construction_correct_answer(rn2483_instance: RN2483):
    """Tests the RN2483 constructor with a correct answer from the microcontroller"""

    assert rn2483_instance.hw_eui == "example_hw_eui"
    assert rn2483_instance.app_eui == "0123456789012345"
    assert rn2483_instance.app_key == "01234567890123450123456789012345"


def test_bool_to_on_off(rn2483_instance: RN2483):
    """Test the bool to string conversion of the RN2483"""

    rn2483_instance._bool_to_on_off(True) == "on"
    rn2483_instance._bool_to_on_off(True) == "off"


def test_sendbreak(rn2483_instance: RN2483):
    """Tests the sendbreak function of the RN2483"""

    rn2483_instance.send_break_condition()
    assert rn2483_instance.uart_connection.break_send


def test_sys_sleep_invalid_input(rn2483_instance: RN2483):
    """Tests the sys sleep function of the RN2483 with invalid input"""

    with pytest.raises(RN2483InvalidInput):
        rn2483_instance.sys_sleep(0)

    with pytest.raises(RN2483InvalidInput):
        rn2483_instance.sys_sleep(4294967297)


def test_sys_sleep_valid_input(rn2483_instance: RN2483):
    """Tests the sys sleep function of the RN2483 with valid input"""

    rn2483_instance.sys_sleep(100)
    assert rn2483_instance.uart_connection.last_written_bytes == b"sys sleep 100\r\n"


def test_sys_get_ver(rn2483_instance: RN2483):
    """Tests the sys get ver function of the RN2483"""

    assert rn2483_instance.sys_get_ver() == "demoversion"


def test_mac_reset(rn2483_instance: RN2483):
    """Tests the reset function for the mac"""

    rn2483_instance.mac_reset(15)
    assert rn2483_instance.uart_connection.last_written_bytes == b"mac reset 15\r\n"


def test_mac_set_deveui(rn2483_instance: RN2483):
    """Tests the mac set deveui function"""

    rn2483_instance.mac_set_deveui("deveui")
    assert (
        rn2483_instance.uart_connection.last_written_bytes
        == b"mac set deveui deveui\r\n"
    )


def test_mac_set_appeui_invalid_input(rn2483_instance: RN2483):
    """Tests the mac set appeui function with invalid input"""

    with pytest.raises(RN2483InvalidInput):
        rn2483_instance.mac_set_appeui("wrong")


def test_mac_set_appeui_valid_input(rn2483_instance: RN2483):
    """Tests the mac set appeui with valid input"""

    rn2483_instance.mac_set_appeui("0123456789012345")
    assert (
        rn2483_instance.uart_connection.last_written_bytes
        == b"mac set appeui 0123456789012345\r\n"
    )


def test_mac_set_appkey_invalid_input(rn2483_instance: RN2483):
    """Tests the mac set appkey function with invalid input"""

    with pytest.raises(RN2483InvalidInput):
        rn2483_instance.mac_set_appkey("wrong")


def test_mac_set_appkey_valid_input(rn2483_instance: RN2483):
    """Tests the mac set appkey with valid input"""

    rn2483_instance.mac_set_appkey("01234567890123450123456789012345")
    assert (
        rn2483_instance.uart_connection.last_written_bytes
        == b"mac set appkey 01234567890123450123456789012345\r\n"
    )


def test_mac_set_pwridx_invalid_input(rn2483_instance: RN2483):
    """Tests the mac set pwridx with invalid input"""

    with pytest.raises(RN2483InvalidInput):
        rn2483_instance.mac_set_pwridx(-1)

    with pytest.raises(RN2483InvalidInput):
        rn2483_instance.mac_set_pwridx(6)


def test_mac_set_pwridx_valid_inpunt(rn2483_instance: RN2483):
    """Tests the mac set pwridx with valid input"""

    rn2483_instance.mac_set_pwridx(4)
    assert rn2483_instance.uart_connection.last_written_bytes == b"mac set pwridx 4\r\n"


def test_mac_set_dr_invalid_input(rn2483_instance: RN2483):
    """Tests the mac set dr with invalid input"""

    with pytest.raises(RN2483InvalidInput):
        rn2483_instance.mac_set_dr(-1)

    with pytest.raises(RN2483InvalidInput):
        rn2483_instance.mac_set_dr(8)


def test_mac_set_dr_valid_inpunt(rn2483_instance: RN2483):
    """Tests the mac set dr with valid input"""

    rn2483_instance.mac_set_dr(4)
    assert rn2483_instance.uart_connection.last_written_bytes == b"mac set dr 4\r\n"


def test_mac_set_adr(rn2483_instance: RN2483):
    """Tests the mac set adr function"""

    rn2483_instance.mac_set_adr(True)
    assert rn2483_instance.uart_connection.last_written_bytes == b"mac set adr on\r\n"


def test_mac_set_ar(rn2483_instance: RN2483):
    """Tests the mac set ar function"""

    rn2483_instance.mac_set_ar(True)
    assert rn2483_instance.uart_connection.last_written_bytes == b"mac set ar on\r\n"


def test_radio_set_pwr_invalid_input(rn2483_instance: RN2483):
    """Tests the radio set pwr function with invalid input"""

    with pytest.raises(RN2483InvalidInput):
        rn2483_instance.radio_set_pwr(2)

    with pytest.raises(RN2483InvalidInput):
        rn2483_instance.radio_set_pwr(16)


def test_radio_set_pwr_valid_input(rn2483_instance: RN2483):
    """Tests the radio set pwd function with valid input"""

    rn2483_instance.radio_set_pwr(5)
    assert rn2483_instance.uart_connection.last_written_bytes == b"radio set pwr 5\r\n"


def test_mac_save(rn2483_instance: RN2483):
    """Tests the mac save function"""

    rn2483_instance.mac_save()
    assert rn2483_instance.uart_connection.last_written_bytes == b"mac save\r\n"


def test_send(rn2483_instance: RN2483):
    """Test the send function"""

    rn2483_instance.send("PeterMaffay")
    assert (
        rn2483_instance.uart_connection.last_written_bytes
        == b"mac tx uncnf 1 50657465724d6166666179\r\n"
    )


def test_initialize_ttn_otaa(rn2483_instance: RN2483):
    """Tests the TTN OTAA"""

    rn2483_instance.initialize_ttn_otaa()
    assert rn2483_instance.uart_connection.last_written_bytes == b"mac join otaa\r\n"


def test_rn2483_invalid_response():
    """Tests the RN2483 invalid response object"""

    exc: RN2483InvalidResponse = RN2483InvalidResponse("Test")
    assert str(exc) == "Test"


def test_execute_with_wrong_answer(rn2483_instance: RN2483):
    """Tests the execution with a single answer"""

    with pytest.raises(RN2483InvalidResponse):
        machine.MOCK_CONFIGURATION = machine.MockConfiguration.WRONG_ANSWERS
        assert rn2483_instance.execute("test")


def test_execute_multiple_with_wrong_answer(rn2483_instance: RN2483):
    """Tests the multiple answer execution"""

    rn2483_instance.uart_connection.mac_join_read = 0
    with pytest.raises(RN2483InvalidResponse):
        machine.MOCK_CONFIGURATION = machine.MockConfiguration.WRONG_ANSWERS
        rn2483_instance.execute_multiple("mac join otaa")


def test_execute_multiple_no_response(rn2483_instance: RN2483):
    """Tests the multiple answer execution with no response"""

    with pytest.raises(RN2483NoResponseError):
        machine.MOCK_CONFIGURATION = machine.MockConfiguration.NO_ANSWER
        rn2483_instance.execute_multiple("mac join otaa")


def test_poll_until_ready_with_invalid_param(rn2483_instance: RN2483):
    """Tests the multiple answer execution"""

    rn2483_instance._poll_until_ready()
