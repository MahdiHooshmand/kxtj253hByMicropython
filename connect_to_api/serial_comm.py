"""
serial_comm.py

This module provides the SerialComm class which handles the serial connection
and sensor initialization using the provided API commands.
"""

import serial
import time

class SerialComm:
    """
    Handles serial communication with the sensor device.
    """

    def __init__(self, sensor_name: str, scale_range: int, odr: int, port: str, baudrate: int = 115200, timeout: float = 1):
        """
        Initialize the SerialComm instance.

        Parameters:
            sensor_name (str): Name of the sensor.
            scale_range (int): Sensor scale range.
            odr (int): Data Output Rate (converted value).
            port (str): Serial port to connect to.
            baudrate (int): Baud rate for the connection.
            timeout (float): Timeout for the serial connection.
        """
        self.sensor_name = sensor_name
        self.scale_range = scale_range
        self.odr = odr
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None

    def connect(self):
        """
        Connect to the sensor via the serial port and initialize it using API commands.

        Raises:
            Exception: If any error occurs during connection or initialization.
        """
        # Check if the sensor type is supported
        if self.sensor_name != 'kionix':
            raise Exception("Selected sensor is under development. Please select a different sensor type.")

        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            self.ser.reset_input_buffer()

            # Read initial lines until an empty line is received
            while True:
                line = self.ser.readline().decode('utf-8').strip()
                if line == '':
                    break

            # Send API import command
            self.ser.write(b'import API\r\n')
            line = self.ser.readline().decode('utf-8').strip()
            if 'import API' in line:
                # Initialize sensor with scale_range and odr
                cmd = f'API.init_sensor(API.acc_range[{self.scale_range}],API.odr[{self.odr}])\r\n'
                self.ser.write(cmd.encode())
                line = self.ser.readline().decode('utf-8').strip()
                if line == f'>>> API.init_sensor(API.acc_range[{self.scale_range}],API.odr[{self.odr}])':
                    # Check sensor identity
                    self.ser.write(b'API.check_who_am_i()\r\n')
                    line = self.ser.readline().decode('utf-8').strip()
                    if line == '>>> API.check_who_am_i()':
                        line = self.ser.readline().decode('utf-8').strip()
                        if line == 'True':
                            # Start reading acceleration data
                            cmd = f'API.read_accel({self.scale_range})\r\n'
                            self.ser.write(cmd.encode())
                            line = self.ser.readline().decode('utf-8').strip()
                            if line == f'>>> API.read_accel({self.scale_range})':
                                return  # Successful connection and initialization
                            else:
                                self.disconnect()
                                raise Exception("Error in API.read_accel command.")
                        else:
                            self.disconnect()
                            raise Exception("Sensor identification failed.")
                    else:
                        self.disconnect()
                        raise Exception("Error in API.check_who_am_i command.")
                else:
                    self.disconnect()
                    raise Exception("Error in API.init_sensor command.")
            else:
                self.disconnect()
                raise Exception("Error importing API.")
        except serial.SerialException as e:
            raise Exception(f"Serial connection error: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error: {e}")

    def disconnect(self):
        """
        Disconnect from the sensor and close the serial port.
        """
        if self.ser:
            try:
                # Send Ctrl+C and Ctrl+D to terminate sensor API commands
                self.ser.write(b'\x03')  # Ctrl+C
                self.ser.write(b'\x04')  # Ctrl+D
                self.ser.reset_input_buffer()
                time.sleep(1)
                self.ser.close()
            except Exception:
                pass
            finally:
                self.ser = None

    def read_line(self) -> str:
        """
        Read a line of data from the serial port.

        Returns:
            str: The decoded line from the serial buffer, or an empty string if no data is available.
        """
        if self.ser and self.ser.in_waiting:
            try:
                return self.ser.readline().decode('utf-8').strip()
            except Exception as e:
                raise Exception(f"Error reading data: {e}")
        return ""
