import machine

from rn2483.rn2483 import RN2483


if __name__ == "__main__":

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
