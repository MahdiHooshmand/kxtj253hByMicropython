# Documentation for Sensor Application and I2C Accelerometer Sensor

This documentation describes two projects:

1. **Real-Time Sensor Application**  
   A desktop application that reads acceleration data via USB from a sensor device and plots it in real time using PyQt5 and PyQtGraph. The application has been refactored into multiple modules with a dedicated data acquisition thread, downsampling, and optimized plotting.

2. **I2C Accelerometer Sensor (MicroPython)**  
   A MicroPython API for initializing and reading data from the KXTJ3-1057 accelerometer sensor over I2C. The API includes functions to initialize the sensor, verify connectivity, and continuously read acceleration data.

---

## Table of Contents

- [Real-Time Sensor Application](#real-time-sensor-application)  
  - [Overview](#overview)  
  - [File Structure](#file-structure)  
  - [Installation](#installation)  
  - [Running the Application](#running-the-application)  
  - [Code Overview](#code-overview)  
  - [Features and Improvements](#features-and-improvements)

- [I2C Accelerometer Sensor (MicroPython)](#i2c-accelerometer-sensor-micropython)  
  - [Overview](#overview-1)  
  - [Requirements and Hardware Setup](#requirements-and-hardware-setup)  
  - [Code Explanation](#code-explanation)  
  - [Running the MicroPython Code](#running-the-micropython-code)

- [Final Note](#final-note)

---

## Real-Time Sensor Application

### Overview

This desktop application reads acceleration data (X, Y, Z) from a sensor device via USB. It displays the data in real time using PyQtGraph within a PyQt5 GUI. To handle high-speed data, the application decouples serial data acquisition into a separate thread, down-samples the data by averaging every five points, and updates the plot every 200 milliseconds.

### File Structure

The code has been split into several modules for clarity and maintainability:

- **`gui_utils.py`**  
  Contains helper functions for displaying warning and error message boxes.

- **`serial_comm.py`**  
  Manages the serial connection and sensor initialization with API commands.

- **`sensor_app.py`**  
  Implements the main GUI application, including the data acquisition thread, downsampling, and plotting.

- **`main.py`**  
  Entry point that creates and runs the application.

### Installation

#### Prerequisites
- Python 3.x  
- A sensor device sending acceleration data via USB  
- A system capable of running PyQt5 applications

#### Install Required Libraries

1. **Update Package Lists and Install pip (if needed):**

   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip
   ```

2. **(Optional) Create a Virtual Environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python Dependencies:**

   ```bash
   pip install pyqtgraph PyQt5 pyserial numpy
   ```

### Running the Application

1. Place all the project files (`gui_utils.py`, `serial_comm.py`, `sensor_app.py`, and `main.py`) in the same directory.

2. Connect your sensor device to an available USB port.

3. Update the port selection in the application if necessary.

4. Launch the application with:

   ```bash
   python main.py
   ```

### Code Overview

#### `gui_utils.py`
Provides helper functions for displaying message boxes.

```python
def show_development_message(parent=None):
    """
    Display a warning message indicating that the selected sensor feature is under development.
    """
    # Implementation code here

def show_error_message(message, parent=None):
    """
    Display an error message.
    """
    # Implementation code here
```

#### `serial_comm.py`
Handles the serial communication with the sensor device.

```python
class SerialComm:
    def __init__(self, sensor_name: str, scale_range: int, port: str, baudrate: int = 115200, timeout: float = 1):
        # Initialization code here
    
    def connect(self):
        """
        Connect to the sensor and initialize it via API commands.
        """
        # Connection and initialization code here
    
    def disconnect(self):
        """
        Disconnect and close the serial port.
        """
        # Disconnection code here

    def read_line(self) -> str:
        """
        Read and return a line from the serial port.
        """
        # Read line code here
```

#### `sensor_app.py`
Defines the main application with a decoupled data acquisition thread, downsampling, and optimized bulk plotting.

Key points include:
- **Data Acquisition Thread:**  
  The `read_serial_data` method continuously reads data and enqueues it in a thread‑safe queue.
  
- **Downsampling:**  
  Every 5 data points are averaged to generate one plot point.
  
- **Optimized Plotting:**  
  The averaged data is stored in NumPy arrays and the plot is updated every 200 ms via a QTimer.

```python
def read_serial_data(self):
    """
    Continuously read serial data in a separate thread and enqueue valid data.
    """
    # Thread loop reading and enqueueing data
    ...

def update_plot(self):
    """
    Process data from the queue, average every 5 points, and update the plot every 200 ms.
    """
    # Dequeue, downsample, and update plot code
    ...
```

#### `main.py`
Starts the PyQt application.

```python
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = SensorApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
```

### Features and Improvements

- **Decoupled Data Acquisition:**  
  Serial data is read in a separate thread to avoid UI blocking.

- **Downsampling:**  
  Only one plot point is generated per every 5 raw data points (using averaging).

- **Optimized Plotting:**  
  Conversion of data buffers into NumPy arrays for efficient bulk updates.

- **Controlled Update Interval:**  
  The plot is refreshed every 200 milliseconds, ensuring smooth performance even with high data rates.

---

## I2C Accelerometer Sensor (MicroPython)

### Overview

This project uses MicroPython to interface with the KXTJ3-1057 accelerometer sensor via I2C. The provided API initializes the sensor, verifies connectivity, and continuously reads acceleration data, printing the values in units of *g*.

### Requirements and Hardware Setup

#### Requirements
- A MicroPython-supported board (e.g., ESP32, STM32, etc.)
- KXTJ3-1057 Accelerometer Sensor

#### Hardware Setup
- **I2C Pins:**  
  - **SCL:** Pin 18  
  - **SDA:** Pin 19
- **I2C Frequency:** 400 kHz

### Code Explanation

The following functions are provided in **`API.py`**:

```python
from machine import I2C, Pin
import time

# Configure I2C
i2c = I2C(1, scl=Pin(18), sda=Pin(19), freq=400000)

# Sensor address and register definitions
address = 0x0E
CTRL_REG1 = 0x1B
CTRL_REG2 = 0x1D
WHO_AM_I = 0x0F

# Available acceleration ranges and their corresponding register values
acc_range = {
    2:  0b11000000,
    4:  0b11001000,
    8:  0b11010000,
    16: 0b11000100
}

def init_sensor(ctrl_reg1_value):
    """
    Initialize the KXTJ3-1057 accelerometer sensor with the given control register value.
    
    Writes to CTRL_REG1 to configure the sensor. A short delay is applied between writes
    to ensure settings take effect.
    """
    i2c.writeto_mem(address, CTRL_REG1, bytes([0b00000000]))
    time.sleep(0.2)
    i2c.writeto_mem(address, CTRL_REG1, bytes([ctrl_reg1_value]))
    time.sleep(0.1)

def check_who_am_i():
    """
    Read the WHO_AM_I register to verify sensor identity.
    
    Returns:
        True if the sensor responds with the expected value (0x35), False otherwise.
    """
    who_am_i = i2c.readfrom_mem(address, WHO_AM_I, 1)[0]
    return who_am_i == 0x35

def read_accel(scale_range):
    """
    Continuously read acceleration data from the sensor and convert it to g values.
    
    Reads 6 bytes starting from register 0x06, processes the raw 16-bit values to 12-bit
    values, applies two's complement conversion for negatives, and scales the values based on
    the selected range.
    
    The sensor output is printed to the console, with a delay of 20 ms between reads.
    """
    time.sleep(2)
    while True:
        data = i2c.readfrom_mem(address, 0x06, 6)
        x_raw = (data[1] << 8) | data[0]
        y_raw = (data[3] << 8) | data[2]
        z_raw = (data[5] << 8) | data[4]
        x = x_raw >> 4
        y = y_raw >> 4
        z = z_raw >> 4
        if x & 0x800:
            x -= 0x1000
        if y & 0x800:
            y -= 0x1000
        if z & 0x800:
            z -= 0x1000
        sensitivity = scale_range / 2048
        x = x * sensitivity
        y = y * sensitivity
        z = z * sensitivity
        print(x, y, z)
        time.sleep_ms(20)
```

### Running the MicroPython Code

1. **Flash MicroPython Firmware**  
   Ensure that your board is running the latest MicroPython firmware.

2. **Hardware Setup**  
   Connect the KXTJ3-1057 sensor to your board using the appropriate I2C pins (SCL: Pin 18, SDA: Pin 19).

3. **Upload the Script**  
   Use tools like ampy, rshell, or WebREPL to upload `API.py` to your board.

4. **Execute the Script**  
   Open a serial terminal and run the script. The sensor data (acceleration in g) will be printed continuously.

---

## Final Note

Both projects illustrate efficient real-time data acquisition techniques:
- The **Real-Time Sensor Application** uses a multithreaded approach with downsampling and optimized plotting to handle high-speed data.
- The **I2C Accelerometer Sensor** project shows how to interface with a sensor using MicroPython for continuous data reading.

Feel free to modify or extend these projects to suit your specific application requirements.
