import API

API.init_sensor(API.acc_range[4],API.odr[256])
API.check_who_am_i()
API.read_accel(4)
