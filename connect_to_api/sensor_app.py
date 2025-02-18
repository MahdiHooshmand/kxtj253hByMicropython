"""
sensor_app.py

This module defines the SensorApp class which provides the main UI for
sensor data visualization, decimation, and data saving. Data acquisition is
handled in a separate thread, and the plot is updated every 200ms with decimated data.
"""

import sys
import time
import csv
import os
import threading
import queue
import numpy as np

from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

from serial_comm import SerialComm
import gui_utils


class SensorApp(QtWidgets.QWidget):
    """
    Main application class for sensor data visualization and saving.
    Data acquisition is performed in a separate thread, and the plot is updated every 200ms.
    """
    def __init__(self):
        super().__init__()
        self.serial_comm = None
        self.timer = None  # Timer for updating the plot
        self.data_queue = queue.Queue()  # Thread-safe queue for incoming serial data
        self.data_thread = None  # Thread for reading serial data

        # Buffers for decimation (raw points for aggregation)
        self.decimation_buffer = []  # Will hold tuples of (time, x, y, z)

        # Buffers for plotting (after decimation)
        self.plot_time = []
        self.plot_x = []
        self.plot_y = []
        self.plot_z = []

        # Base time for plotting
        self.start_time = None

        # Variables for data saving
        self.save_file_path = ''
        self.is_saving = False
        self.start_time_saving = None

        self.init_ui()

    def init_ui(self):
        """
        Initialize the user interface.
        """
        # Main layout
        main_layout = QtWidgets.QVBoxLayout()

        # Horizontal layout for input controls
        input_layout = QtWidgets.QHBoxLayout()

        # Sensor name selection
        sensor_label = QtWidgets.QLabel('Sensor Name:')
        self.sensor_combo = QtWidgets.QComboBox()
        self.sensor_combo.addItems(['IMP', 'kionix'])
        input_layout.addWidget(sensor_label)
        input_layout.addWidget(self.sensor_combo)

        # Sensor scale selection
        scale_label = QtWidgets.QLabel('Sensor Scale:')
        self.scale_combo = QtWidgets.QComboBox()
        self.scale_combo.addItems(['2', '4', '8', '16'])
        input_layout.addWidget(scale_label)
        input_layout.addWidget(self.scale_combo)

        # USB port selection
        port_label = QtWidgets.QLabel('USB Port:')
        self.port_combo = QtWidgets.QComboBox()
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        port_list = [port.device for port in ports]
        self.port_combo.addItems(port_list)
        input_layout.addWidget(port_label)
        input_layout.addWidget(self.port_combo)

        # Connect/Disconnect button
        self.connect_button = QtWidgets.QPushButton('Connect')
        self.connect_button.clicked.connect(self.connect_clicked)
        input_layout.addWidget(self.connect_button)

        main_layout.addLayout(input_layout)

        # PyQtGraph widget for real-time plotting
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setTitle("Sensor Acceleration Over Time")
        self.plot_widget.setLabel('left', 'Acceleration', units='g')
        self.plot_widget.setLabel('bottom', 'Time', units='s')
        main_layout.addWidget(self.plot_widget)

        # Plot curves for X, Y, Z axes
        self.curve_x = self.plot_widget.plot(pen=pg.mkPen(color='r', width=2), name='X')
        self.curve_y = self.plot_widget.plot(pen=pg.mkPen(color='g', width=2), name='Y')
        self.curve_z = self.plot_widget.plot(pen=pg.mkPen(color='b', width=2), name='Z')
        self.plot_widget.addLegend()

        # Horizontal layout for data saving controls
        save_layout = QtWidgets.QHBoxLayout()

        # Save file selection button
        self.save_button = QtWidgets.QPushButton('Save To')
        self.save_button.clicked.connect(self.select_save_file)
        save_layout.addWidget(self.save_button)

        # File path display label
        self.file_path_label = QtWidgets.QLabel('File Path:')
        save_layout.addWidget(self.file_path_label)

        # Start/Stop saving button
        self.start_button = QtWidgets.QPushButton('Start')
        self.start_button.clicked.connect(self.start_stop_saving)
        self.start_button.setEnabled(False)  # Disabled until a file is selected
        save_layout.addWidget(self.start_button)

        main_layout.addLayout(save_layout)

        self.setLayout(main_layout)
        self.setWindowTitle('Sensor and USB Port Selection')
        self.show()

    def select_save_file(self):
        """
        Open a dialog to select the file path for saving data.
        """
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Select File Path and Name", "", "CSV Files (*.csv);;All Files (*)", options=options
        )
        if file_name:
            self.save_file_path = file_name
            self.file_path_label.setText(f'File Path: {self.save_file_path}')
            self.start_button.setEnabled(True)

    def start_stop_saving(self):
        """
        Start or stop saving sensor data to a file.
        """
        if not self.is_saving:
            # Start saving
            self.is_saving = True
            self.start_time_saving = None  # Reset start time for saving
            self.start_button.setText('Stop')

            # Write header information in the CSV file
            with open(self.save_file_path, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(['Sensor Name:', self.sensor_combo.currentText()])
                csvwriter.writerow(['Scale Range:', self.scale_combo.currentText()])
                csvwriter.writerow(['Serial Port:', self.port_combo.currentText()])
                csvwriter.writerow(['File Name:', os.path.basename(self.save_file_path)])
                csvwriter.writerow(['Time', 'X', 'Y', 'Z'])
        else:
            # Stop saving
            self.is_saving = False
            self.start_button.setText('Start')
            QtWidgets.QMessageBox.information(
                self, "Saving Completed", f"Data saved to file:\n{self.save_file_path}"
            )

    def connect_clicked(self):
        """
        Handle the connect button click event.
        """
        sensor_name = self.sensor_combo.currentText()
        scale_range = int(self.scale_combo.currentText())
        usb_port = self.port_combo.currentText()

        try:
            self.serial_comm = SerialComm(sensor_name, scale_range, usb_port)
            self.serial_comm.connect()

            # Set sensor scale and adjust plot Y-axis range
            self.scale_range = scale_range
            self.plot_widget.setYRange(-self.scale_range, self.scale_range)

            # Change button to Disconnect
            self.connect_button.setText('Disconnect')
            self.connect_button.clicked.disconnect()
            self.connect_button.clicked.connect(self.disconnect_clicked)

            # Initialize base time and start data acquisition thread
            self.start_time = time.time()
            self.data_thread = threading.Thread(target=self.read_serial_data, daemon=True)
            self.data_thread.start()

            # Start timer to update the plot every 200ms
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.update_plot)
            self.timer.start(200)

        except Exception as e:
            gui_utils.show_error_message(str(e), self)

    def disconnect_clicked(self):
        """
        Handle the disconnect button click event.
        """
        if self.serial_comm:
            self.serial_comm.disconnect()
            self.serial_comm = None

        # Stop the timer
        if self.timer:
            self.timer.stop()
            self.timer = None

        # Clear all buffers and plot curves
        self.decimation_buffer.clear()
        self.plot_time.clear()
        self.plot_x.clear()
        self.plot_y.clear()
        self.plot_z.clear()
        self.curve_x.clear()
        self.curve_y.clear()
        self.curve_z.clear()

        # Change button back to Connect
        self.connect_button.setText('Connect')
        self.connect_button.clicked.disconnect()
        self.connect_button.clicked.connect(self.connect_clicked)

        # Disable Start button for saving
        self.start_button.setEnabled(False)
        self.is_saving = False
        self.start_button.setText('Start')

    def read_serial_data(self):
        """
        Continuously read serial data in a separate thread and put valid data into a queue.
        """
        while self.serial_comm and self.serial_comm.ser is not None:
            data = self.serial_comm.read_line()
            if data:
                values = data.split()
                if len(values) == 3:
                    try:
                        x, y, z = map(float, values)
                        t = time.time() - self.start_time
                        self.data_queue.put((t, x, y, z))
                    except Exception as e:
                        print("Error parsing data:", e)
            else:
                time.sleep(0.01)  # Avoid busy-waiting

    def update_plot(self):
        """
        Process new data from the queue, perform decimation (average every 5 points),
        update the plot, and save raw data if saving is enabled.
        """
        rows_to_write = []
        # Process all available data from the queue
        while not self.data_queue.empty():
            try:
                t, x, y, z = self.data_queue.get_nowait()
            except queue.Empty:
                break

            # If saving is enabled, prepare data row (using elapsed time since saving started)
            if self.is_saving:
                if self.start_time_saving is None:
                    self.start_time_saving = time.time()
                elapsed = time.time() - self.start_time_saving
                rows_to_write.append([elapsed, x, y, z])

            # Add the data point to the decimation buffer
            self.decimation_buffer.append((t, x, y, z))
            # If there are at least 5 data points, average them to form one plot point
            if len(self.decimation_buffer) >= 5:
                group = self.decimation_buffer[:5]
                self.decimation_buffer = self.decimation_buffer[5:]
                avg_t = sum(pt[0] for pt in group) / len(group)
                avg_x = sum(pt[1] for pt in group) / len(group)
                avg_y = sum(pt[2] for pt in group) / len(group)
                avg_z = sum(pt[3] for pt in group) / len(group)
                self.plot_time.append(avg_t)
                self.plot_x.append(avg_x)
                self.plot_y.append(avg_y)
                self.plot_z.append(avg_z)

        # Write the accumulated rows to the CSV file if saving is enabled
        if rows_to_write:
            try:
                with open(self.save_file_path, 'a', newline='') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerows(rows_to_write)
            except Exception as e:
                print("Error writing to CSV:", e)

        # Remove decimated points older than 5 seconds
        current_time = time.time() - self.start_time
        time_threshold = current_time - 5
        new_plot_time = []
        new_plot_x = []
        new_plot_y = []
        new_plot_z = []
        for t, x, y, z in zip(self.plot_time, self.plot_x, self.plot_y, self.plot_z):
            if t >= time_threshold:
                new_plot_time.append(t)
                new_plot_x.append(x)
                new_plot_y.append(y)
                new_plot_z.append(z)
        self.plot_time = new_plot_time
        self.plot_x = new_plot_x
        self.plot_y = new_plot_y
        self.plot_z = new_plot_z

        # Update the plot using NumPy arrays for efficient bulk updates
        if self.plot_time:  # Only update if there is data
            self.curve_x.setData(np.array(self.plot_time), np.array(self.plot_x))
            self.curve_y.setData(np.array(self.plot_time), np.array(self.plot_y))
            self.curve_z.setData(np.array(self.plot_time), np.array(self.plot_z))

    def closeEvent(self, event):
        """
        Handle the window close event to ensure proper disconnection.
        """
        self.disconnect_clicked()
        event.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = SensorApp()
    sys.exit(app.exec_())
