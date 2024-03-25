import bluetooth
import struct
import time
import machine
import ubinascii
from ble_advertising import advertising_payload
from micropython import const
from machine import Pin

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_INDICATE_DONE = const(20)

_FLAG_READ = const(0x0002)
_FLAG_NOTIFY = const(0x0010)
_FLAG_INDICATE = const(0x0020)

_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
_TEMP_CHAR = (
    bluetooth.UUID(0x2A6E),
    _FLAG_READ | _FLAG_NOTIFY | _FLAG_INDICATE,
)
_ENV_SENSE_SERVICE = (
    _ENV_SENSE_UUID,
    (_TEMP_CHAR,),
)

PIN_1 = 20
PIN_2 = 18

led = Pin("LED", Pin.OUT)


class BLEConnection:
    def __init__(self, ble):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle,),) = self._ble.gatts_register_services((_ENV_SENSE_SERVICE,))
        self._connections = set()
        name = (
            "pico-%s"
            % ubinascii.hexlify(self._ble.config("mac")[1], ":").decode().upper()
        )
        print("Central name %s" % name)
        self._payload = advertising_payload(name=name, services=[_ENV_SENSE_UUID])
        self._advertise()

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()
        elif event == _IRQ_GATTS_INDICATE_DONE:
            conn_handle, value_handle, status = data

    def send_data(self, data):
        self._ble.gatts_write(self._handle, struct.pack("<h", int(data)))
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._handle)

    def _advertise(self, interval_us=100):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)


held_down = False


def detect_buttons(max_time=None):
    global held_down, led
    button1 = machine.Pin(PIN_1, machine.Pin.IN, machine.Pin.PULL_DOWN)
    button2 = machine.Pin(PIN_2, machine.Pin.IN, machine.Pin.PULL_DOWN)
    start_time = time.time()
    while max_time is None or start_time - time.time() <= max_time:
        if not held_down and button1.value() == 1:
            led.off()
            held_down = True
            return 1
        if not held_down and button2.value() == 1:
            led.off()
            held_down = True
            return -1
        if button2.value() != 1 and button1.value() != 1:
            led.on()
            held_down = False


def main():
    led.on()
    ble = bluetooth.BLE()
    connection = BLEConnection(ble)
    led.off()
    while True:
        button = detect_buttons()
        print("[INFO] Button", button, "pressed, sending data...")
        connection.send_data(button)


if __name__ == "__main__":
    main()

