"""This module mocks the machine library from micropython"""

from enum import Enum

class MockConfiguration(Enum):
    """Holds the different mock configurations"""

    CORRECT_ANSWERS = 0
    WRONG_ANSWERS = 1
    NO_ANSWER = 2


MOCK_CONFIGURATION: MockConfiguration = MockConfiguration.NO_ANSWER
CORRECT_ANSWERS: dict[bytes, bytes] = {
    b"sys get hweui\r\n": b"example_hw_eui",
    b"sys get ver\r\n": b"demoversion",
    b"mac reset 15\r\n": b"ok",
    b"mac set deveui deveui\r\n": b"ok",
    b"mac set appeui 0123456789012345\r\n": b"ok",
    b"mac set appkey 01234567890123450123456789012345\r\n": b"ok",
    b"mac set pwridx 4\r\n": b"ok",
    b"mac set pwridx 1\r\n": b"ok",
    b"mac set adr on\r\n": b"ok",
    b"mac set adr off\r\n": b"ok",
    b"mac set ar on\r\n": b"ok",
    b"mac set ar off\r\n": b"ok",
    b"mac reset 868\r\n": b"ok",
    b"radio set pwr 5\r\n": b"ok",
    b"mac save\r\n": b"ok",
    b"mac set dr 4\r\n": b"ok",
    b"mac set dr 5\r\n": b"ok",
    b"mac tx uncnf 1 50657465724d6166666179\r\n": b"ok",
    b"mac set deveui example_hw_eui\r\n": b"ok",
    b"mac join otaa\r\n": b"ok",
}
WRONG_ANSWER: bytes = b"invalid_param"


class UART:
    """Mocks the micropython UART class"""

    last_written_bytes: bytes = None
    break_send: bool = False
    mac_join_read: int = 0
    sys_get_hweui: bool = False

    def __init__(self, *args, **kwargs) -> None:
        """Mocks the constructor of the UART class"""

        pass

    def write(self, *args, **kwargs) -> None:
        """Mocks the write function of the UART class"""

        self.last_written_bytes = args[0]

    def _read(self) -> bytes:
        """Mocks all read function from the UART class"""

        if MOCK_CONFIGURATION == MockConfiguration.CORRECT_ANSWERS:
            if (
                self.last_written_bytes == b"mac join otaa\r\n"
                and self.mac_join_read == 0
            ):
                self.mac_join_read += 1
            elif (
                self.last_written_bytes == b"mac join otaa\r\n"
                and self.mac_join_read == 1
            ):
                self.mac_join_read += 1
                return b"accepted"
            elif (
                self.last_written_bytes == b"mac join otaa\r\n"
                and self.mac_join_read == 2
            ):
                return None
            if (
                self.last_written_bytes == b"sys get hweui\r\n"
                and not self.sys_get_hweui
            ):
                self.sys_get_hweui = True
                return b"invalid_param"
            return CORRECT_ANSWERS[self.last_written_bytes]
        elif MOCK_CONFIGURATION == MockConfiguration.WRONG_ANSWERS:
            if self.last_written_bytes == b"mac join otaa\r\n" and (
                self.mac_join_read == 0 or self.mac_join_read == 1
            ):
                self.mac_join_read += 1
                return b"wrong"
            elif (
                self.last_written_bytes == b"mac join otaa\r\n"
                and self.mac_join_read == 2
            ):
                return None
            return WRONG_ANSWER
        else:
            return None

    def readline(self, *args, **kwargs) -> bytes:
        """Mocks the readline function of the UART class"""

        return self._read()

    def read(self, *args, **kwargs) -> bytes:
        """Mocks the read function of the UART class"""

        return self._read()

    def sendbreak(self, *args, **kwargs) -> None:
        """Mocks the sendbreak function of the UART class"""

        self.break_send = True


class Pin:
    """Mocks the micropython Pin class"""

    OUT: int = 1

    def __init__(self, *args, **kwargs) -> None:
        """Mocks the constructor of the Pin class"""

        pass

    def high(self) -> None:
        """Mocks the high function of the Pin class"""

        pass

    def low(self) -> None:
        """Mocks the low function of the Pin class"""

        pass


class WDT:
    """Mocks the micropython watchdog class"""

    def __init__(self, *args, **kwargs) -> None:
        """Mocks the constructor of the watchdog class"""

        pass

    def feed(self, *args, **kwargs) -> None:
        """Mocks the feed function of the watchdog"""

        pass
