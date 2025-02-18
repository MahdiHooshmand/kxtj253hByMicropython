"""
main.py

Entry point for the sensor application.
"""

import sys
from PyQt5 import QtWidgets
from sensor_app import SensorApp

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = SensorApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
