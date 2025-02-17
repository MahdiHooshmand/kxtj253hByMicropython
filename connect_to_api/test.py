import sys
import serial
import serial.tools.list_ports
import time
import csv
import os
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg


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
        self.ser = None
        self.timer = None  # تایمر برای به‌روزرسانی نمودار
        self.data_x = []
        self.data_y = []
        self.data_z = []
        self.time_data = []
        self.start_time = None
        self.scale_range = None  # ذخیره مقیاس سنسور

        # متغیرهای مربوط به ذخیره‌سازی داده‌ها
        self.save_file_path = ''
        self.is_saving = False

        self.init_ui()

    def init_ui(self):
        # تنظیمات لایه‌بندی اصلی
        main_layout = QtWidgets.QVBoxLayout()

        # لایه افقی برای ورودی‌ها
        input_layout = QtWidgets.QHBoxLayout()

        # انتخاب نام سنسور
        sensor_label = QtWidgets.QLabel('نام سنسور:')
        self.sensor_combo = QtWidgets.QComboBox()
        self.sensor_combo.addItems(['IMP', 'kionix'])

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

        # دکمه‌ی Connect/Disconnect
        self.connect_button = QtWidgets.QPushButton('Connect')
        self.connect_button.clicked.connect(self.connect_clicked)

        # اضافه کردن دکمه‌ها به لایه ورودی
        input_layout.addWidget(self.connect_button)

        # اضافه کردن لایه‌ها به لایه اصلی
        main_layout.addLayout(input_layout)

        # ایجاد ویجت نمودار PyQtGraph
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setTitle("شتاب سنسور بر حسب زمان")
        self.plot_widget.setLabel('left', 'شتاب', units='g')
        self.plot_widget.setLabel('bottom', 'زمان', units='s')
        main_layout.addWidget(self.plot_widget)

        # خطوط نمودار برای X, Y, Z
        self.curve_x = self.plot_widget.plot(pen=pg.mkPen(color='r', width=2), name='X')
        self.curve_y = self.plot_widget.plot(pen=pg.mkPen(color='g', width=2), name='Y')
        self.curve_z = self.plot_widget.plot(pen=pg.mkPen(color='b', width=2), name='Z')

        # نمایش افسانه (legend)
        self.plot_widget.addLegend()

        # لایه افقی برای دکمه‌های ذخیره‌سازی
        save_layout = QtWidgets.QHBoxLayout()

        # دکمه‌ی Save To
        self.save_button = QtWidgets.QPushButton('Save To')
        self.save_button.clicked.connect(self.select_save_file)
        save_layout.addWidget(self.save_button)

        # نمایش مسیر فایل ذخیره‌سازی
        self.file_path_label = QtWidgets.QLabel('مسیر فایل:')
        save_layout.addWidget(self.file_path_label)

        # دکمه‌ی Start/Stop
        self.start_button = QtWidgets.QPushButton('Start')
        self.start_button.clicked.connect(self.start_stop_saving)
        self.start_button.setEnabled(False)  # تا زمانی که فایل انتخاب نشده، غیرفعال است
        save_layout.addWidget(self.start_button)

        # اضافه کردن لایه ذخیره‌سازی به لایه اصلی
        main_layout.addLayout(save_layout)

        self.setLayout(main_layout)
        self.setWindowTitle('انتخاب سنسور و پورت USB')
        self.show()

    def select_save_file(self):
        # باز کردن دیالوگ برای انتخاب مسیر و نام فایل
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, "انتخاب مسیر و نام فایل", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            self.save_file_path = file_name
            self.file_path_label.setText(f'مسیر فایل: {self.save_file_path}')
            self.start_button.setEnabled(True)  # فعال کردن دکمه Start

    def start_stop_saving(self):
        if not self.is_saving:
            # شروع ذخیره‌سازی
            self.is_saving = True
            self.start_time_saving = None  # زمان شروع ذخیره‌سازی
            self.start_button.setText('Stop')

            # نوشتن مشخصات در خط اول فایل
            with open(self.save_file_path, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(['Sensor Name:', self.sensor_combo.currentText()])
                csvwriter.writerow(['Scale Range:', self.scale_combo.currentText()])
                csvwriter.writerow(['Serial Port:', self.port_combo.currentText()])
                csvwriter.writerow(['File Name:', os.path.basename(self.save_file_path)])
                csvwriter.writerow(['Time', 'X', 'Y', 'Z'])  # هدر ستون‌ها
        else:
            # توقف ذخیره‌سازی
            self.is_saving = False
            self.start_button.setText('Start')

            # نمایش فایل ذخیره‌شده
            QtWidgets.QMessageBox.information(self, "ذخیره‌سازی کامل شد", f"داده‌ها در فایل زیر ذخیره شدند:\n{self.save_file_path}")

    def connect_clicked(self):
        sensor_name = self.sensor_combo.currentText()
        scale_range = int(self.scale_combo.currentText())
        usb_port = self.port_combo.currentText()

        if sensor_name != 'kionix':
            show_development_message()
            return
        else:
            BAUDRATE = 115200
            try:
                self.ser = serial.Serial(usb_port, BAUDRATE, timeout=1)
                # پاکسازی بافر ورودی
                self.ser.reset_input_buffer()

                # ذخیره مقیاس سنسور و تنظیم محور Y
                self.scale_range = scale_range
                self.plot_widget.setYRange(-self.scale_range, self.scale_range)

                # خواندن خطوط ابتدایی
                while True:
                    l = self.ser.readline().decode('utf-8').strip()
                    if l == '':
                        break

                self.ser.write(b'import API\r\n')
                l = self.ser.readline().decode('utf-8').strip()
                if 'import API' in l:
                    cmd = f'API.init_sensor(API.acc_range[{scale_range}])\r\n'
                    self.ser.write(cmd.encode())
                    l = self.ser.readline().decode('utf-8').strip()
                    if l == f'>>> API.init_sensor(API.acc_range[{scale_range}])':
                        self.ser.write(b'API.check_who_am_i()\r\n')
                        l = self.ser.readline().decode('utf-8').strip()
                        if l == '>>> API.check_who_am_i()':
                            l = self.ser.readline().decode('utf-8').strip()
                            if l == 'True':
                                cmd = f'API.read_accel({scale_range})\r\n'
                                self.ser.write(cmd.encode())
                                l = self.ser.readline().decode('utf-8').strip()
                                if l == f'>>> API.read_accel({scale_range})':
                                    # تغییر دکمه به Disconnect
                                    self.connect_button.setText('Disconnect')
                                    self.connect_button.clicked.disconnect()
                                    self.connect_button.clicked.connect(self.disconnect_clicked)

                                    # شروع تایمر برای به‌روزرسانی نمودار
                                    self.start_time = time.time()
                                    self.timer = QtCore.QTimer()
                                    self.timer.timeout.connect(self.update_plot)
                                    self.timer.start(50)  # هر 50 میلی‌ثانیه یکبار به‌روزرسانی می‌شود
                                else:
                                    self.show_error_message("خطا در API.read_accel")
                                    self.stop_serial()
                                    return
                            else:
                                self.show_error_message("سنسور قابل شناسایی نیست.")
                                self.stop_serial()
                                return
                        else:
                            self.show_error_message("خطا در API.check_who_am_i")
                            self.stop_serial()
                            return
                    else:
                        self.show_error_message("خطا در API.init_sensor")
                        self.stop_serial()
                        return
                else:
                    self.show_error_message("خطا در import API")
                    self.stop_serial()
                    return
            except serial.SerialException as e:
                self.show_error_message(f"خطا در اتصال سریال: {e}")
            except Exception as e:
                self.show_error_message(f"خطای غیرمنتظره: {e}")

    def disconnect_clicked(self):
        # ارسال Ctrl+C و Ctrl+D
        if self.ser:
            self.ser.write(b'\x03')  # Ctrl+C
            self.ser.write(b'\x04')  # Ctrl+D
            self.ser.reset_input_buffer()
            time.sleep(1)
            self.ser.close()
            self.ser = None

        # متوقف کردن تایمر
        if self.timer:
            self.timer.stop()
            self.timer = None

        # پاکسازی داده‌ها
        self.data_x.clear()
        self.data_y.clear()
        self.data_z.clear()
        self.time_data.clear()
        self.curve_x.clear()
        self.curve_y.clear()
        self.curve_z.clear()

        # تغییر دکمه به Connect
        self.connect_button.setText('Connect')
        self.connect_button.clicked.disconnect()
        self.connect_button.clicked.connect(self.connect_clicked)

        # غیرفعال کردن دکمه Start
        self.start_button.setEnabled(False)
        self.is_saving = False
        self.start_button.setText('Start')

    def update_plot(self):
        if self.ser and self.ser.in_waiting:
            try:
                data = self.ser.readline().decode('utf-8').strip()
                if data:
                    # فرض می‌کنیم داده‌ها به صورت سه عدد جداشده با فاصله هستند
                    values = data.split()
                    if len(values) == 3:
                        x, y, z = map(float, values)
                        # فیلتر کردن داده‌های خارج از محدوده
                        if (-self.scale_range <= x <= self.scale_range and
                            -self.scale_range <= y <= self.scale_range and
                            -self.scale_range <= z <= self.scale_range):
                            current_time = time.time() - self.start_time
                            self.time_data.append(current_time)
                            self.data_x.append(x)
                            self.data_y.append(y)
                            self.data_z.append(z)

                            # **فیلتر کردن داده‌ها برای نگه‌داشتن تنها ۵ ثانیه آخر**
                            time_threshold = current_time - 5  # ۵ ثانیه قبل
                            while self.time_data and self.time_data[0] < time_threshold:
                                self.time_data.pop(0)
                                self.data_x.pop(0)
                                self.data_y.pop(0)
                                self.data_z.pop(0)

                            # به‌روزرسانی نمودار
                            self.curve_x.setData(self.time_data, self.data_x)
                            self.curve_y.setData(self.time_data, self.data_y)
                            self.curve_z.setData(self.time_data, self.data_z)

                            # ذخیره‌سازی داده‌ها در فایل
                            if self.is_saving:
                                if self.start_time_saving is None:
                                    self.start_time_saving = time.time()  # زمان شروع ذخیره‌سازی
                                elapsed_time = time.time() - self.start_time_saving
                                with open(self.save_file_path, 'a', newline='') as csvfile:
                                    csvwriter = csv.writer(csvfile)
                                    csvwriter.writerow([elapsed_time, x, y, z])
                        else:
                            # اگر داده خارج از محدوده باشد، آن را نادیده می‌گیریم
                            pass
                    else:
                        print(f"داده نامعتبر دریافت شد: '{data}'")
            except Exception as e:
                print(f"خطا در دریافت داده: {e}")

    def stop_serial(self):
        if self.timer:
            self.timer.stop()
            self.timer = None
        if self.ser:
            self.ser.write(b'\x03')  # Ctrl+C
            self.ser.write(b'\x04')  # Ctrl+D
            time.sleep(1)
            self.ser.close()
            self.ser = None

    def show_error_message(self, message):
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Critical)
        msg_box.setWindowTitle("خطا")
        msg_box.setText(message)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg_box.exec_()

    def closeEvent(self, event):
        # متوقف کردن تایمر و بستن پورت سریال در هنگام بستن برنامه
        self.disconnect_clicked()
        event.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = SensorApp()
    sys.exit(app.exec_())
