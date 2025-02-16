# Documentation for Serial Plotter and I2C Accelerometer Sensor Codes

This documentation covers two projects:

1. **Real-Time Serial Data Plotting with PyQtGraph (Serial Plotter)**  
   A desktop application that reads acceleration data from a serial port and displays it in real-time using PyQtGraph with a PyQt5 graphical interface.

2. **I2C Accelerometer Sensor (MicroPython)**  
   A MicroPython script that initializes and reads data from the KXTJ3-1057 accelerometer sensor via I2C and prints acceleration values in units of *g*.

---

## Table of Contents

- [Real-Time Serial Data Plotting with PyQtGraph](#real-time-serial-data-plotting-with-pyqtgraph)
  - [Introduction](#introduction)
  - [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Installing Required Libraries](#installing-required-libraries)
    - [Resolving Qt Platform Plugin Error](#resolving-qt-platform-plugin-error)
  - [Code Explanation](#code-explanation)
    - [Overview](#overview)
    - [Imports and Serial Port Setup](#imports-and-serial-port-setup)
    - [SerialPlotter Class](#serialplotter-class)
      - [Initialization (`__init__`)](#initialization-__init__)
      - [User Interface Setup (`initUI`)](#user-interface-setup-initui)
      - [Plot Update Method (`update_plot`)](#plot-update-method-update_plot)
      - [Clean Exit Handling (`closeEvent`)](#clean-exit-handling-closeevent)
    - [Main Execution Block](#main-execution-block)
  - [Usage](#usage)
  - [Conclusion](#conclusion)
- [I2C Accelerometer Sensor (MicroPython)](#i2c-accelerometer-sensor-micropython)
  - [Description](#description)
  - [Requirements](#requirements)
  - [Hardware Setup](#hardware-setup)
  - [Setup and Usage](#setup-and-usage)
  - [Code Structure Overview](#code-structure-overview)
  - [Conclusion](#conclusion-1)
- [Final Note](#final-note)

---

## Real-Time Serial Data Plotting with PyQtGraph

### Introduction
This project demonstrates how to read acceleration data (X, Y, Z) from a serial port and plot it in real-time using Python. The code reads data from a serial device (like a microcontroller with sensors) and displays it with a graphical interface using PyQtGraph—a fast plotting library suitable for real-time applications.

### Installation

#### Prerequisites
- **Python 3.x**
- A serial device sending data in the format `(x, y, z)` over serial communication.
- A system capable of running PyQt5 applications.

#### Installing Required Libraries
Update Package Lists and Install Dependencies:

```bash
sudo apt-get update
sudo apt-get install python3-pip
```

(Optional) Create a Virtual Environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required Python libraries:

```bash
pip install pyqtgraph PyQt5 pyserial
```

#### Resolving Qt Platform Plugin Error
If you encounter the following error:

```pgsql
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
This application failed to start because no Qt platform plugin could be initialized.
```

Follow these steps:

1. **Install Missing Qt and X11 Dependencies:**

    ```bash
    sudo apt-get install --reinstall libxcb-xinerama0
    sudo apt-get install libxcb-xinput0 libxcb-icccm4 libxcb-image0 \
    libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 \
    libxcb-sync1 libxcb-xfixes0 libxkbcommon-x11-0
    ```

2. **Ensure Qt5 Development Packages Are Installed:**

    ```bash
    sudo apt-get install qt5-default qt5-qmake qtbase5-dev qtbase5-dev-tools
    ```

3. **Set the QT_QPA_PLATFORM Environment Variable:**

    ```bash
    export QT_QPA_PLATFORM=xcb
    ```

4. **Reinstall PyQt5 if Necessary:**

    ```bash
    pip uninstall PyQt5
    pip install PyQt5
    ```

5. **Clear Qt Plugin Cache:**

    ```bash
    rm -rf ~/.cache/Qt* ~/.config/QtProject
    ```

6. **Switch to Xorg Session (If Using Wayland):**
- Log out of your current session.
- On the login screen, select your user and choose "GNOME on Xorg" (or a similar option).
- Log in normally.

After these steps, rerun your Python script. The GUI should now display without errors.

### Code Explanation
#### Overview
The Python script reads acceleration data (X, Y, Z) from a serial port and plots it in real-time using PyQtGraph. The GUI updates continuously, displaying the most recent data points.
#### Imports and Serial Port Setup

```python
import sys
import serial
import time
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

# Initialize the serial port
ser = serial.Serial('/dev/ttyACM0', 115200)  # Replace with your serial port (e.g., 'COM3' on Windows)
```

- **sys:** Access to system-specific parameters.
- **serial:** For serial communication.
- **time:** Handling time-related functions.
- **PyQt5 modules:** Creating the GUI application.
- **pyqtgraph:** Plotting data in real-time.

#### SerialPlotter Class
This class creates the main window and handles data reading and plotting.
##### Initialization (`__init__`)

```python
def __init__(self):
    super().__init__()

    # Data storage
    self.x_data = []
    self.y_data = []
    self.z_data = []
    self.t_data = []

    self.max_points = 1000  # Maximum number of data points to display

    # Setup UI
    self.initUI()

    # Timer for updating the plot
    self.timer = QtCore.QTimer()
    self.timer.timeout.connect(self.update_plot)
    self.timer.start(10)  # Update every 10 milliseconds
```

- Initializes lists to store incoming acceleration data.
- Calls `initUI()` to set up the user interface.
- Creates a QTimer that periodically calls `update_plot()` to refresh the plot.

##### User Interface Setup (`initUI`)

```python
def initUI(self):
    # Central widget
    self.central_widget = QtWidgets.QWidget()
    self.setCentralWidget(self.central_widget)

    # Layout
    self.layout = QtWidgets.QVBoxLayout()
    self.central_widget.setLayout(self.layout)

    # Plot widget
    self.plot_widget = pg.PlotWidget()
    self.layout.addWidget(self.plot_widget)

    self.plot_widget.addLegend()

    # Plot lines
    self.line_x = self.plot_widget.plot(self.t_data, self.x_data, pen=pg.mkPen('r', width=2), name='X')
    self.line_y = self.plot_widget.plot(self.t_data, self.y_data, pen=pg.mkPen('g', width=2), name='Y')
    self.line_z = self.plot_widget.plot(self.t_data, self.z_data, pen=pg.mkPen('b', width=2), name='Z')

    # Plot settings
    self.plot_widget.setLabel('left', 'Acceleration', units='g')
    self.plot_widget.setLabel('bottom', 'Time', units='s')
    self.plot_widget.showGrid(True, True)
```

- Sets up the main window and layout.
- Initializes the plot widget and adds it to the layout.
- Creates plot lines for X, Y, and Z data with different colors.
- Configures labels and enables grid display.

##### Plot Update Method (`update_plot`)

```python
def update_plot(self):
    try:
        line = ser.readline().decode('utf-8').strip()
        print(f"Received data: {line}")

        if line.count(',') == 2:
            x, y, z = map(float, line.strip('()').split(','))
            t = time.time()

            if not self.t_data:
                self.t0 = t  # Initial time reference

            # Append new data
            self.x_data.append(x)
            self.y_data.append(y)
            self.z_data.append(z)
            self.t_data.append(t - self.t0)  # Time elapsed since start

            # Limit data lists to max_points
            if len(self.x_data) > self.max_points:
                self.x_data = self.x_data[-self.max_points:]
                self.y_data = self.y_data[-self.max_points:]
                self.z_data = self.z_data[-self.max_points:]
                self.t_data = self.t_data[-self.max_points:]

            # Update plot data
            self.line_x.setData(self.t_data, self.x_data)
            self.line_y.setData(self.t_data, self.y_data)
            self.line_z.setData(self.t_data, self.z_data)

            # Adjust plot range
            self.plot_widget.setXRange(self.t_data[0], self.t_data[-1], padding=0)

            # Adjust Y-axis range if necessary
            ymin = min(min(self.x_data), min(self.y_data), min(self.z_data)) - 0.1
            ymax = max(max(self.x_data), max(self.y_data), max(self.z_data)) + 0.1
            self.plot_widget.setYRange(ymin, ymax, padding=0)
        else:
            print(f"Invalid data received: {line}")

    except Exception as e:
        print(f"Error: {e}")
```

- Reads a line from the serial port and decodes it.
- Validates and parses the acceleration data.
- Appends new data points and limits the data lists to a maximum number of points.
- Updates the plot lines and adjusts the axes dynamically.
- Handles exceptions gracefully.

##### Clean Exit Handling (`closeEvent`)

```python
def closeEvent(self, event):
    ser.close()
    event.accept()
```

- Closes the serial port when the application window is closed.

#### Main Execution Block

```python
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = SerialPlotter()
    window.show()
    sys.exit(app.exec_())
```

- Creates the Qt application.
- Instantiates the `SerialPlotter` class and displays the main window.
- Enters the application's event loop.

### Usage
1. **Connect Your Serial Device**

    Ensure your device is connected and sending data in the format (x, y, z) over the serial port.
2.  **Modify the Serial Port Path**
    Update the serial port path in the code to match your system:
    
    ```python
    ser = serial.Serial('/dev/ttyACM0', 115200)
    ```
- On Windows, it might be COM3, COM4, etc.
- On Linux or macOS, it might be /dev/ttyUSB0, /dev/ttyS0, etc.
3. **Run the Script**

    Execute:

    ```bash
   python your_script_name.py
    ```
4. **View the Real-Time Plot**

    A window will open displaying the acceleration data in real-time.

5. **Stop the Script**

    Close the window to exit the application and close the serial port gracefully.

### Conclusion

This project provides a complete example of real-time data plotting using Python, PyQt5, and PyQtGraph. The code can be adapted for various sensors or data types, ensuring robust and dynamic visualization of serial data.

## I2C Accelerometer Sensor (MicroPython)
### Description
This MicroPython project configures and reads data from a KXTJ3-1057 accelerometer sensor via I2C. The sensor is set to operate in active mode with 12-bit resolution and a data rate of 1600Hz. The script continuously reads acceleration data and prints the values in units of g.
### Requirements
- A MicroPython-supported board (e.g., ESP32, STM32, etc.)
- KXTJ3-1057 Accelerometer Sensor
- MicroPython firmware installed on the board

### Hardware Setup
- **I2C Pins:**
  - SCL → Pin 18
  - SDA → Pin 19
### Setup and Usage
1. **Flash MicroPython Firmware**

    Ensure your board is running MicroPython.

2. **Connect the Sensor**

    Wire the KXTJ3-1057 sensor to the board using the specified I2C pins.

3. **Upload the Script**

    Use tools such as ampy, rshell, or the WebREPL to upload the script to your board.

4. **Run the Script**

    Execute the script using a serial terminal or the MicroPython REPL. The script will continuously print the acceleration data.

### Code Structure Overview
- **I2C Configuration:**

    Initializes the I2C interface on bus 1 with designated pins and sets the frequency to 400kHz.
- **Sensor Initialization (`init_sensor`):**

    Configures the sensor by:

  - Setting `CTRL_REG1` to activate the sensor and set 12-bit resolution.
  - Setting `DATA_CTRL_REG` for a data rate of 1600Hz.
- **Data Reading (`read_accel`):**
  - Reads 6 bytes of data from the sensor.
  - Combines the bytes to form 16-bit raw values.
  - Converts the raw values to 12-bit values and handles two's complement for negatives.
  - Converts raw data to acceleration in g using the sensor's sensitivity.
- **Main Loop:**

    Continuously reads and prints the acceleration data with a short delay between reads.

### Conclusion
This project demonstrates how to interface with an accelerometer sensor via I2C using MicroPython. The code serves as a starting point for real-time data acquisition projects on microcontrollers and can be easily adapted for other sensors or applications.

---

## Final Note
Both projects illustrate techniques for real-time data acquisition and processing:
- The **Serial Plotter** leverages a desktop application to visualize serial data in real time using PyQtGraph and PyQt5.
- The **I2C Accelerometer** Sensor project demonstrates sensor interfacing and data reading on a microcontroller with MicroPython.

Feel free to modify and expand these projects to suit your specific requirements. EOF
