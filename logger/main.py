import sys
import serial
import time
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

# Configure the serial port
ser = serial.Serial('/dev/ttyACM0', 115200)  # Replace with the appropriate serial port

class SerialPlotter(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize data storage
        self.x_data = []
        self.y_data = []
        self.z_data = []
        self.t_data = []

        self.max_points = 1000  # Maximum number of points to display

        # Set up the UI
        self.initUI()

        # Timer for updating the plot
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(10)  # Update every 10 milliseconds

    def initUI(self):
        # Create central widget
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        # Set layout
        self.layout = QtWidgets.QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Create plot widget
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)

        self.plot_widget.addLegend()

        # Define plot lines
        self.line_x = self.plot_widget.plot(self.t_data, self.x_data, pen=pg.mkPen('r', width=2), name='X')
        self.line_y = self.plot_widget.plot(self.t_data, self.y_data, pen=pg.mkPen('g', width=2), name='Y')
        self.line_z = self.plot_widget.plot(self.t_data, self.z_data, pen=pg.mkPen('b', width=2), name='Z')

        # Configure plot labels and grid
        self.plot_widget.setLabel('left', 'Acceleration', units='g')
        self.plot_widget.setLabel('bottom', 'Time', units='s')
        self.plot_widget.showGrid(True, True)

    def update_plot(self):
        try:
            line = ser.readline().decode('utf-8').strip()
            print(f"Received data: {line}")

            # Ensure data is correctly formatted
            if line.count(',') == 2:
                x, y, z = map(float, line.strip('()').split(','))
                t = time.time()

                if not self.t_data:
                    self.t0 = t  # Set initial timestamp

                # Append new data
                self.x_data.append(x)
                self.y_data.append(y)
                self.z_data.append(z)
                self.t_data.append(t - self.t0)

                # Limit stored data points
                if len(self.x_data) > self.max_points:
                    self.x_data = self.x_data[-self.max_points:]
                    self.y_data = self.y_data[-self.max_points:]
                    self.z_data = self.z_data[-self.max_points:]
                    self.t_data = self.t_data[-self.max_points:]

                # Update plot lines
                self.line_x.setData(self.t_data, self.x_data)
                self.line_y.setData(self.t_data, self.y_data)
                self.line_z.setData(self.t_data, self.z_data)

                # Adjust x-axis range
                self.plot_widget.setXRange(self.t_data[0], self.t_data[-1], padding=0)

                # Adjust y-axis range dynamically
                ymin = min(min(self.x_data), min(self.y_data), min(self.z_data)) - 0.1
                ymax = max(max(self.x_data), max(self.y_data), max(self.z_data)) + 0.1
                self.plot_widget.setYRange(ymin, ymax, padding=0)
            else:
                print(f"Invalid data received: {line}")

        except Exception as e:
            print(f"Error: {e}")

    def closeEvent(self, event):
        # Close the serial port on exit
        ser.close()
        event.accept()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = SerialPlotter()
    window.show()
    sys.exit(app.exec_())
