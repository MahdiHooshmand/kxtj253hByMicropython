from machine import I2C, Pin
import time

# Configure I2C
i2c = I2C(1, scl=Pin(18), sda=Pin(19), freq=400000)

# Sensor address
address = 0x0E

# Register addresses
CTRL_REG1 = 0x1B
CTRL_REG2 = 0x1D
DATA_CTRL_REG = 0x21
WHO_AM_I = 0x0F

acc_range = {
    2: 0b11000000,
    4: 0b11001000,
    8: 0b11010000,
    16: 0b11000100
}

odr = {
    1:0b00001000,
    2:0b00001001,
    4:0b00001010,
    8:0b00001011,
    16:0b00000000,
    32:0b00000001,
    64:0b00000010,
    128:0b00000011,
    256:0b00000100,
    512:0b00000101,
    1024:0b00000110,
    2048:0b00000111
}

def init_sensor(ctrl_reg1_value,data_ctrl_reg_value):
    """Initialize the KXTJ3-1057 accelerometer sensor with given register values."""
    # Write CTRL_REG1
    i2c.writeto_mem(address, CTRL_REG1, bytes([0b00000000]))
    time.sleep(0.2)
    i2c.writeto_mem(address, DATA_CTRL_REG, bytes([data_ctrl_reg_value]))
    time.sleep(0.2)
    i2c.writeto_mem(address, CTRL_REG1, bytes([ctrl_reg1_value]))

    # # Write CTRL_REG2
    # i2c.writeto_mem(address, CTRL_REG2, bytes([ctrl_reg2_value]))

    # Short delay to apply settings
    time.sleep(0.1)

def check_who_am_i():
    """Check WHO_AM_I register to verify connection."""
    who_am_i = i2c.readfrom_mem(address, WHO_AM_I, 1)[0]
    if who_am_i == 0x35:
        return True
    else:
        return False

def read_accel(scale_range):
    if scale_range == 2:
        scale_range = 1.999
    elif scale_range == 4:
        scale_range = 3.998
    elif scale_range == 8:
        scale_range = 7.996
    elif scale_range == 16:
        scale_range = 15.992
    """Read acceleration data from the sensor and convert it to g values."""
    # Read 6 bytes of acceleration data
    time.sleep(2)

    # Store previous values
    prev_x, prev_y, prev_z = None, None, None

    while True:
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

        # Convert to acceleration in g
        sensitivity = scale_range / 2048  # حساسیت بر اساس رنج انتخابی
        x = x * sensitivity
        y = y * sensitivity
        z = z * sensitivity

        # Check if values have changed
        if (x, y, z) != (prev_x, prev_y, prev_z):
            print( x, y, z)
            prev_x, prev_y, prev_z = x, y, z
