import ctypes
import time
from smbus2 import SMBus
from ctypes import *

I2C_ADDR = 0x77
I2C_BUS = 1

# load BSEC2 library
bsec = ctypes.CDLL("libbsec2.so")

# BSEC data structures (simplified)
class bsec_outputs(Structure):
    _fields_ = [
        ("iaq", c_float),
        ("static_iaq", c_float),
        ("co2_equivalent", c_float),
        ("breath_voc_equivalent", c_float),
        ("comp_temperature", c_float),
        ("comp_humidity", c_float),
        ("raw_pressure", c_float),
        ("raw_temperature", c_float),
        ("raw_humidity", c_float),
        ("gas_resistance", c_float),
        ("stab_status", c_uint8),
        ("run_status", c_uint8),
    ]

# i2c helper functions
bus = SMBus(I2C_BUS)

@CFUNCTYPE(c_int8, c_uint8, c_uint8, POINTER(c_uint8), c_uint16)
def i2c_read(dev_id, reg_addr, data, length):
    rx = bus.read_i2c_block_data(dev_id, reg_addr, length)
    for i in range(length):
        data[i] = rx[i]
    return 0

@CFUNCTYPE(c_int8, c_uint8, c_uint8, POINTER(c_uint8), c_uint16)
def i2c_write(dev_id, reg_addr, data, length):
    payload = [data[i] for i in range(length)]
    bus.write_i2c_block_data(dev_id, reg_addr, payload)
    return 0

@CFUNCTYPE(None, c_uint32, c_void_p)
def delay_us(period, _):
    time.sleep(period / 1_000_000)

# init BSEC2
bsec.bsec_init()
bsec.bsec_set_i2c_callbacks(i2c_read, i2c_write, delay_us)

# load standard configuration (depends on BSEC package)
bsec.bsec_load_configuration(b"bsec_sel_iaq.json")

# measurement loop
print("BSEC2 running (VOC, IAQ, CO2)...\n")

outputs = bsec_outputs()

while True:
    status = bsec.bsec_do_steps(byref(outputs))

    if status == 0:  # BSEC_OK
        print(f"VOC (breath equivalent): {outputs.breath_voc_equivalent:.2f} ppm")
        print(f"IAQ:                    {outputs.iaq:.1f}")
        print(f"Static IAQ:             {outputs.static_iaq:.1f}")
        print(f"CO2 equivalent:         {outputs.co2_equivalent:.1f} ppm")
        print(f"Temperature:            {outputs.comp_temperature:.2f} °C")
        print(f"Humidity:               {outputs.comp_humidity:.2f} %")
        print(f"Pressure:               {outputs.raw_pressure/100:.2f} hPa\n")

    time.sleep(3)
