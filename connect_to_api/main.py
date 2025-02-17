import time
import serial

import sys
import serial.tools.list_ports
from PyQt5 import QtWidgets

PORT = "/dev/ttyACM0"
BAUDRATE = 115200
ser = serial.Serial(PORT, BAUDRATE, timeout=1)

def run(acc_range):
    while True:
        l = ser.readline().decode('utf-8').strip()
        if l == '':
            break
        else:
            print(l)
    ser.write(b'import API\r\n')
    l = ser.readline().decode('utf-8').strip()
    if 'import API' in l:
        ser.write(b'API.init_sensor(API.acc_range[%d])\r\n' % acc_range)
        l = ser.readline().decode('utf-8').strip()
        if l == f'>>> API.init_sensor(API.acc_range[{acc_range}])':
            ser.write(b'API.check_who_am_i()\r\n')
            l = ser.readline().decode('utf-8').strip()
            if l == '>>> API.check_who_am_i()':
                l = ser.readline().decode('utf-8').strip()
                if l == 'True':
                    ser.write(b'API.read_accel(%d)\r\n' % acc_range)
                    l = ser.readline().decode('utf-8').strip()
                    if l == f'>>> API.read_accel({acc_range})':
                        while True:
                            print(ser.readline().decode('utf-8').strip())
                    else:
                        print(1,l)
                        ser.write(b'\x03')
                        ser.write(b'\x04')
                        time.sleep(2)
                        return
                else:
                    print(2,l)
                    ser.write(b'\x03')
                    ser.write(b'\x04')
                    time.sleep(2)
                    return
            else:
                print(3,l)
                ser.write(b'\x03')
                ser.write(b'\x04')
                time.sleep(2)
                return
        else:
            print(4,l)
            ser.write(b'\x03')
            ser.write(b'\x04')
            time.sleep(2)
            return
    else:
        print(5,l)
        ser.write(b'\x03')
        ser.write(b'\x04')
        time.sleep(2)
        return


def output_function(sensor_name, scale_range, usb_port):
    if sensor_name != 'KYONIX':
        show_development_message()
    else:
        PORT = usb_port

def show_development_message():
    # ایجاد دیالوگ‌باکس برای نمایش پیغام
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Warning)
    msg_box.setWindowTitle("در حال توسعه")
    msg_box.setText("متاسفانه این بخش از نرم‌افزار در حال توسعه است.\nلطفا نوع دیگری از سنسورها را انتخاب بفرمایید.")
    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg_box.exec_()

class SensorApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # تنظیمات لایه‌بندی اصلی
        main_layout = QtWidgets.QVBoxLayout()

        # لایه افقی برای ورودی‌ها
        input_layout = QtWidgets.QHBoxLayout()

        # انتخاب نام سنسور
        sensor_label = QtWidgets.QLabel('نام سنسور:')
        self.sensor_combo = QtWidgets.QComboBox()
        self.sensor_combo.addItems(['IMP', 'KYONIX'])

        # اضافه کردن به لایه ورودی
        input_layout.addWidget(sensor_label)
        input_layout.addWidget(self.sensor_combo)

        # انتخاب مقیاس سنسور
        scale_label = QtWidgets.QLabel('مقیاس سنسور:')
        self.scale_combo = QtWidgets.QComboBox()
        self.scale_combo.addItems(['2', '4', '8', '16'])

        # اضافه کردن به لایه ورودی
        input_layout.addWidget(scale_label)
        input_layout.addWidget(self.scale_combo)

        # نمایش لیست پورت‌های USB
        port_label = QtWidgets.QLabel('پورت USB:')
        self.port_combo = QtWidgets.QComboBox()
        ports = serial.tools.list_ports.comports()
        port_list = [port.device for port in ports]
        self.port_combo.addItems(port_list)

        # اضافه کردن به لایه ورودی
        input_layout.addWidget(port_label)
        input_layout.addWidget(self.port_combo)

        # دکمه‌ی Connect
        connect_button = QtWidgets.QPushButton('Connect')
        connect_button.clicked.connect(self.connect_clicked)

        # اضافه کردن لایه‌ها به لایه اصلی
        main_layout.addLayout(input_layout)
        main_layout.addWidget(connect_button)

        self.setLayout(main_layout)
        self.setWindowTitle('انتخاب سنسور و پورت USB')
        self.show()

    def connect_clicked(self):
        sensor_name = self.sensor_combo.currentText()
        scale_range = int(self.scale_combo.currentText())
        usb_port = self.port_combo.currentText()
        output_function(sensor_name, scale_range, usb_port)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = SensorApp()
    sys.exit(app.exec_())

# while True:
#     run(4)