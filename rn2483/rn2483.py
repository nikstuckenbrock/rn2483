"""
This module contains a wrapper class to use the RN2483 LoRaWAN module.
Use https://ww1.microchip.com/downloads/en/DeviceDoc/40001784B.pdf for reference.
"""

from binascii import hexlify

from machine import UART, WDT, Pin
from utime import sleep_ms


class RN2483InvalidInput(Exception):
    """This exception is raised if there was an invalid input parameter"""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class RN2483NoResponseError(Exception):
    """This exception is raised when there was no response from the RN2483 controller"""

    def __init__(
        self,
        message: str = "There was an error receiving a response from the RN2483, consider increasing the UART timeout and check the physical connection.",
    ) -> None:
        super().__init__(message)


class RN2483InvalidResponse(Exception):
    """This response is raised when the response validation fails"""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class RN2483:
    """Wrapper class for the RN2483 LoRaWAN module"""

    def __init__(
        self,
        uart_id: int,
        tx_pin: int,
        rx_pin: int,
        reset_pin: int,
        app_eui: str,
        app_key: str,
        wdt: WDT,
        baudrate: int = 57600,
        uart_timetout: int = 5000,
        debug: bool = False,
    ) -> None:
        """Initializes a new instance of the RN2483 controller class

        Args:
            uart_id (int): The id of the UART interface on the board
            tx_pin (int): The TX pin number
            rx_pin (int): The RX pin number
            reset_pin (int): The reset pin number
            app_eui (str): The AppEUI to use for OTAA
            app_key (str): The AppKey to use for OTAA
            wdt (WDT): The watchdog object to feed
            baudrate (int, optional): The baudrate to use. Defaults to 57600.
            uart_timetout (int, optional): The UART timeout to use. Defaults to 5000.
            debug (bool, optional): Should debug logs be printed? Defaults to False.
        """

        self.uart_connection: UART = UART(
            uart_id,
            baudrate=baudrate,
            tx=Pin(tx_pin),
            rx=Pin(rx_pin),
            timeout=uart_timetout,
        )
        self.reset_pin: Pin = Pin(reset_pin, mode=Pin.OUT)
        self.app_eui = app_eui
        self.app_key = app_key
        self.wdt = wdt
        self.debug = debug
        self.reset()
        self._poll_until_ready()

    def _poll_until_ready(self):
        """Polls the controller until it gets a valid response"""

        self.wdt.feed()
        while self.sys_get_hweui() == "invalid_param":
            sleep_ms(10)
            self.sys_get_hweui()
            self.wdt.feed()
        self.uart_connection.read()
        self.wdt.feed()

    def _print(self, text: str):
        """Prints text to the console if the debug mode is enabled

        Args:
            text (str): The text ot print
        """

        if self.debug:
            print(text)

    def _bool_to_on_off(self, on: bool) -> str:
        """Converts a boolean value to the string the controller needs

        Args:
            on (bool): The boolean value

        Returns:
            str: The string for the controller
        """

        return "on" if on else "off"

    def reset(self, wait_in_ms: int = 500):
        """Resets the controller using the specified reset pin

        Args:
            wait_in_ms (int, optional): The milliseconds to wait between high and low. Defaults to 10.
        """

        self._print("[RN2483.reset] Starting reset ...")
        self.reset_pin.high()
        sleep_ms(wait_in_ms)
        self.wdt.feed()
        self.reset_pin.low()
        sleep_ms(wait_in_ms)
        self.wdt.feed()
        self.reset_pin.high()
        sleep_ms(wait_in_ms)
        self.wdt.feed()
        self._print("[RN2483.reset] Reset finished!")

    def send_break_condition(self):
        """Sends a break condition to e.g. wake up the controller"""

        self.uart_connection.sendbreak()
        self._poll_until_ready()

    def sys_sleep(self, length: int):
        """Sets the system to sleep for the specified length

        Args:
            length (int): The length in milliseconds

        Raises:
            RN2483InvalidInput: If the sleeping time is invalid
        """

        if length < 100 or length > 4294967296:
            raise RN2483InvalidInput(
                message="The length to sleep must be between 100 and 4294967296!"
            )

        self.uart_connection.write(bytes(f"sys sleep {length}" + "\r\n", "utf-8"))
        self.wdt.feed()

    def execute(self, command: str, validate: bool = True, valid: str = "ok") -> str:
        """Executes a given command and waits for a sinlge response

        Args:
            command (str): The command to execute
            validate (bool): Should the response be validated?
            valid (str): The valid response string

        Returns:
            str: The response of the command
        """

        self.wdt.feed()
        self.uart_connection.write(bytes(command + "\r\n", "utf-8"))
        sleep_ms(100)
        self.wdt.feed()
        response = self.uart_connection.readline()
        self._print(f"[RN2483.execute] Command: {command}, Raw response: {response}")
        if not response:
            raise RN2483NoResponseError()
        decoded: str = response.decode("utf-8").strip()  # type: ignore
        if validate and decoded != valid:
            raise RN2483InvalidResponse(
                message=f"The response {decoded} didn't match the exptected {valid}!"
            )
        self.wdt.feed()
        return decoded

    def execute_multiple(
        self, command: str, validate: bool = True, valid: list[str] = ["ok", "accepted"]
    ) -> list[str]:
        """Executes a command with multiple responses

        Args:
            command (str): The command to execute
            validate (bool, optional): Should the responses be validated? Defaults to True.
            valid (list[str], optional): The valid responses (ordered). Defaults to ["ok", "accepted"].

        Raises:
            RN2483NoResponseError: If there was no response
            RN2483InvalidResponse: If the response was not valid

        Returns:
            list[str]: The responses as a list
        """

        self.wdt.feed()
        self.uart_connection.write(bytes(command + "\r\n", "utf-8"))
        sleep_ms(5000)
        self.wdt.feed()
        results: list[str] = []
        response = self.uart_connection.readline()
        self._print(f"[RN2483.execute] Command: {command}, Raw response: {response}")
        if not response:
            raise RN2483NoResponseError()
        decoded: str = response.decode("utf-8").strip()  # type: ignore
        results.append(decoded)
        while response is not None:
            self.wdt.feed()
            sleep_ms(5000)
            response = self.uart_connection.readline()
            self.wdt.feed()
            if response:
                decoded: str = response.decode("utf-8").strip()  # type: ignore
                results.append(decoded)
        if validate and results != valid:
            raise RN2483InvalidResponse(
                message=f"The response {results} didn't match the exptected {valid}!"
            )
        return results

    def sys_get_ver(self) -> str:
        """Returns version related information

        Returns:
            str: A string containing version information
        """

        return self.execute("sys get ver", validate=False)

    def sys_get_hweui(self) -> str:
        """Returns and sets the local hardware EUI

        Returns:
            str: The hardware EUI
        """
        self.hw_eui = self.execute("sys get hweui", validate=False)
        self._print(f"[sys get hweui] {self.hw_eui}")
        return self.hw_eui

    def mac_reset(self, band: int):
        """Resets the given band

        Args:
            band (int): The band to use
        """

        self.execute(f"mac reset {str(band)}", validate=False)

    def mac_set_deveui(self, deveui: str):
        """Sets the device EUI

        Args:
            deveui (str): The EUI to set
        """

        self.execute(f"mac set deveui {deveui}")

    def mac_set_appeui(self, appeui: str):
        """Sets the application EUI

        Args:
            appeui (str): The EUI to set

        Raises:
            RN2483InvalidInput: If the AppEUI is not valid
        """

        if len(appeui) != 16:
            raise RN2483InvalidInput("The AppEUI needs to be exact 16 characters long!")

        self.execute(f"mac set appeui {appeui}")

    def mac_set_appkey(self, appkey: str):
        """Sets the application key

        Args:
            appkey (str): The key to set

        Raises:
            RN2483InvalidInput: If the AppKey is not valid
        """

        if len(appkey) != 32:
            raise RN2483InvalidInput("The AppKey needs to be exact 32 characters long!")

        self.execute(f"mac set appkey {appkey}")

    def mac_set_pwridx(self, pwrindex: int):
        """Sets the index value for the output power

        Args:
            pwrindex (int): The power index to use

        Raises:
            RN2483InvalidInput: If the power index is invalid
        """

        if pwrindex < 0 or pwrindex > 5:
            raise RN2483InvalidInput(
                message="The power index needs to be between 0 and 5 for 433 MHz and 1 to 5 for 868 MHz!"
            )

        self.execute(f"mac set pwridx {str(pwrindex)}")

    def mac_set_dr(self, datarate: int):
        """Sets the data rate to use

        Args:
            datarate (int): The data rate

        Raises:
            RN2483InvalidInput: If the datarate is invalid
        """

        if datarate < 0 or datarate > 7:
            raise RN2483InvalidInput(
                message="The data rate need to be between 0 and 7!"
            )

        self.execute(f"mac set dr {str(datarate)}")

    def mac_set_adr(self, on: bool):
        """Sets the adaptive data rate feature flag

        Args:
            on (bool): Should the feature be on or off
        """

        value: str = self._bool_to_on_off(on=on)
        self.execute(f"mac set adr {value}")

    def mac_set_ar(self, on: bool):
        """Sets the autoreply feature flag

        Args:
            on (bool): Should the feature be on or off
        """

        value: str = self._bool_to_on_off(on=on)
        self.execute(f"mac set ar {value}")

    def radio_set_pwr(self, index: int):
        """Sets the transceiver output power

        Args:
            index (int): The power index to use

        Raises:
            RN2483InvalidInput: If the power index is invalid
        """

        if index < 3 or index > 15:
            raise RN2483InvalidInput(
                message="The power index must be between 3 and 15!"
            )

        self.execute(f"radio set pwr {str(index)}")

    def mac_save(self):
        """Saves the LoRaWAN class A protocol configuration parameters to the EEPROM"""

        self.execute("mac save")

    def mac_join(self, mode: str):
        """Runs the joining procedure

        Args:
            mode (MacJoinMode): The mode to join
        """

        self.execute_multiple(f"mac join {mode}")

    def send(self, data: str):
        """Sends data to using LoRaWAN

        Args:
            data (str): The data as a string
        """

        encoded = bytes(data, "utf-8")
        buffer = hexlify(encoded).decode("utf-8")
        self.execute(f"mac tx uncnf 1 {buffer}", validate=False)

    def initialize_ttn_otaa(self):
        """Starts the joining procedure for TTN"""

        self.sys_get_hweui()
        sleep_ms(100)
        self.mac_reset(band=868)
        self.mac_set_deveui(deveui=self.hw_eui)
        self.mac_set_appeui(appeui=self.app_eui)
        self.mac_set_appkey(appkey=self.app_key)
        self.mac_set_pwridx(pwrindex=1)
        self.mac_set_dr(datarate=5)
        self.mac_set_adr(on=False)
        self.mac_set_ar(on=False)
        self.mac_save()
        sleep_ms(3000)
        self.wdt.feed()
        self.mac_join(mode="otaa")
        self.wdt.feed()
