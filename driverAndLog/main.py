from machine import I2C, Pin
import time

# Configure I2C
i2c = I2C(1, scl=Pin(18), sda=Pin(19), freq=400000)

# Sensor address
address = 0x0E

# Register addresses
CTRL_REG1 = 0x1B
DATA_CTRL_REG = 0x1D

def init_sensor():
    """Initialize the KXTJ3-1057 accelerometer sensor."""
    # Configure CTRL_REG1
    # Bit 7: PC1 (1 for Active)
    # Bit 6: RES (1 for 12-bit resolution)
    # Bits 4-3: GSEL[1:0] (11 for ±16g range)
    ctrl_reg1_value = 0b11000000  # Equivalent to 0xD8
    i2c.writeto_mem(address, CTRL_REG1, bytes([ctrl_reg1_value]))

    # Configure DATA_CTRL_REG for highest data rate (1600Hz)
    data_ctrl_reg_value = 0x07  # 1600Hz
    i2c.writeto_mem(address, DATA_CTRL_REG, bytes([data_ctrl_reg_value]))

def read_accel():
    """Read acceleration data from the sensor and convert it to g values."""
    # Read 6 bytes of acceleration data
    data = i2c.readfrom_mem(address, 0x06, 6)

    # Combine bytes to form 16-bit raw values
    x_raw = (data[1] << 8) | data[0]
    y_raw = (data[3] << 8) | data[2]
    z_raw = (data[5] << 8) | data[4]

    # Convert to 12-bit values by shifting
    x = x_raw >> 4
    y = y_raw >> 4
    z = z_raw >> 4

    # Handle negative values using two's complement
    if x & 0x800:
        x -= 0x1000
    if y & 0x800:
        y -= 0x1000
    if z & 0x800:
        z -= 0x1000

    # Convert to acceleration in g (±16g range, sensitivity = 16g/2048)
    sensitivity = 16 / 2048  # Equivalent to 0.0078g per LSB
    x = x * sensitivity
    y = y * sensitivity
    z = z * sensitivity

    return (x, y, z)

# Initialize the sensor
init_sensor()

# Short delay to apply settings
time.sleep(0.1)

# Read and print acceleration data in a loop
while True:
    accel_data = read_accel()
    print(accel_data)
    time.sleep_us(1250)
