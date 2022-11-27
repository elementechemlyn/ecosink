import ecoflow 
from typing import Optional

def _btoi(b: Optional[bool]):
    if b is None:
        return 255
    return 1 if b else 0

def build2(dst: int, cmd_set: int, cmd_id: int, data: bytes = b''):
    b = bytes([170, 2])
    b += len(data).to_bytes(2, "little")
    b += ecoflow.calcCrc8(b)
    b += bytes([13, 0, 0, 0, 0, 0, 0, 32, dst, cmd_set, cmd_id])
    b += data
    b += ecoflow.calcCrc16(b)
    return b

def reset():
    return build2(2, 32, 3)

def close(value: int):
    return build2(2, 32, 41, value.to_bytes(2, "little"))

def get_product_info(dst: int):
    return build2(dst, 1, 5)

def get_cpu_id():
    return build2(2, 1, 64)

def get_serial_main():
    return build2(2, 1, 65)

def get_pd():
    return build2(2, 32, 2, b'\0')

def get_lcd():
    return build2(2, 32, 40)

def get_ems_main():
    return build2(3, 32, 2)

def get_inverter():
    return build2(4, 32, 2)

def get_dc_in_type(product: int):
    if ecoflow.is_delta(product):
        cmd = (5, 32, 82)
    else:
        cmd = (4, 32, 68)
    return build2(*cmd, bytes([0]))

def get_dc_in_current(product: int):
    dst = 5 if ecoflow.is_delta(product) else 4
    return build2(dst, 32, 72)

def get_fan_auto():
    return build2(4, 32, 74)

def get_lab():
    return build2(4, 32, 84)

def get_serial_extra():
    return build2(6, 1, 65)

def get_ems_extra():
    return build2(6, 32, 2)

def get_mppt():
    return build2(5, 32, 2)
    
def set_standby_timeout(value: int):
    return build2(2, 32, 33, value.to_bytes(2, "little"))


def set_usb(enable: bool):
    return build2(2, 32, 34, bytes([1 if enable else 0]))


def set_light(product: int, value: int):
    return build2(2, 32, 35, bytes([value]))

def set_dc_out(product: int, enable: bool):
    if ecoflow.is_delta(product):
        cmd = (5, 32, 81)
    elif product == 20:
        cmd = (8, 8, 3)
    elif product in [5, 7, 12, 18]:
        cmd = (2, 32, 34)
    else:
        cmd = (2, 32, 37)
    return build2(*cmd, bytes([1 if enable else 0]))

def set_beep(enable: bool):
    return build2(2, 32, 38, bytes([0 if enable else 1]))

def set_lcd(product: int, time: int = 0xFFFF, light: int = 255):
    arg = time.to_bytes(2, "little")
    if ecoflow.is_delta(product) or ecoflow.is_river_mini(product):
        arg += bytes([light])
    return build2(2, 32, 39, arg)

def set_level_max(product: int, value: int):
    dst = 4 if product == 17 else 3
    return build2(dst, 32, 49, bytes([value]))

def set_level_min(value: int):
    return build2(3, 32, 51, bytes([value]))

def set_generate_start(value: int):
    return build2(3, 32, 52, bytes([value]))

def set_generate_stop(value: int):
    return build2(3, 32, 53, bytes([value]))

def set_ac_in_slow(value: bool):
    return build2(4, 32, 65, bytes([_btoi(value)]))

def set_ac_out(product: int, enable: bool = None, xboost: bool = None, freq: int = 255):
    if product == 20:
        cmd = (8, 8, 2)
        arg = [_btoi(enable)]
    else:
        cmd = (4, 32, 66)
        arg = [_btoi(enable), _btoi(xboost), 255, 255, 255, 255, freq]
    return build2(*cmd, bytes(arg))


def set_dc_in_type(product: int, value: int):
    if ecoflow.is_delta(product):
        cmd = (5, 32, 82)
    else:
        cmd = (4, 32, 67)
    return build2(*cmd, bytes([value]))

def set_ac_in_limit(watts: int = 0xFFFF, pause: bool = None):
    arg = bytes([255, 255])
    arg += watts.to_bytes(2, "little")
    arg += bytes([_btoi(pause)])
    return build2(4, 32, 69, arg)


def set_dc_in_current(product: int, value: int):
    dst = 5 if ecoflow.is_delta(product) else 4
    return build2(dst, 32, 71, value.to_bytes(4, "little"))

def set_fan_auto(product: int, value: bool):
    return build2(4, 32, 73, bytes([1 if value else 3]))

def set_lab(value: int):
    return build2(4, 32, 84, bytes([value]))


def set_ac_timeout(value: int):
    return build2(4, 32, 153, value.to_bytes(2, "little"))

def set_ambient(mode: int = 255, animate: int = 255, color=(255, 255, 255, 255), brightness=255):
    arg = [mode, animate, *color, brightness]
    return build2(6, 32, 97, bytes(arg))


def _set_watt(value: int):
    return build2(8, 8, 7, value.to_bytes(2, "little"))