# RN2483 (MicroPython)

This projects contains a controller class for the [RN2483](https://www.microchip.com/en-us/product/RN2483) LoRaWAN Transceiver module. This code origins from the course [Embedded Systems](https://www.fh-muenster.de/eti/personen/professoren/gloesekoetter/embedded-systems.php) at [FH Münster – University of Applied Sciences](https://www.fh-muenster.de/). It was tested using a RP2040 as a controller to send measurement data.

## Development

To setup your local development environment install [Visual Studio Code](https://code.visualstudio.com/) and the [MicroPico](https://marketplace.visualstudio.com/items?itemName=paulober.pico-w-go) extension. After that connect the Raspberry Pi Pico using a USB cabel and run your code using MicroPico. To enforce a global style please install the [development requirements](./dev.requirements.txt) and after that the pre-commit hook using `pre-commit install`.

## Setup & upload project to Pico

- Download the latest firmware from https://micropython.org/download/RPI_PICO/ and flash the RP2040 via UF2 bootloader
- Follow the steps above to setup a local development environment
- Open the command pallete (```CTRL + SHIFT + P```)
- Search for ```MicroPico: Configure project``` and execute it
- Search for ```MicroPico: Upload project to Pico``` and execute it
- Switch to the ```main.py``` and run it!

## RN2483

To send data create an instance of the `RN2483` class using the following snippet replacing the secrets and pins with your configuration. After creating an instance you'll need to initialize the connection using (in most cases) [OTAA](https://www.thethingsnetwork.org/docs/lorawan/end-device-activation/#over-the-air-activation-in-lorawan-11).

```python
rn2483: RN2483 = RN2483(
    uart_id=0,
    tx_pin=12,
    rx_pin=13,
    reset_pin=10,
    app_eui="<insert_app_eui_here>",
    app_key="<insert_app_key_here>",
    debug=True,
    wdt=machine.WDT(timeout=8000),
)
rn2483.initialize_ttn_otaa()
rn2483.send("Hello World!")
```