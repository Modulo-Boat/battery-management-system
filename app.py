from metrics import Metrics
import flask
import redis
import serial
import subprocess
import threading

class Battery():
  def __init__(self):
    self.metrics = Metrics()
    self.percentage = None
    self.voltage = None
    self.capacity = None
    self.current = None
    self.remaining_sec = None
    self._redis = redis.Redis(host='192.168.1.123', port=30002)

    port="/dev/ttyUSB0"
    self.ser=serial.Serial(port, baudrate=9600,bytesize=8, parity='N', stopbits=1,timeout=0.9)
    fetch_thread = threading.Thread(target=self.fetch_data)
    fetch_thread.start()

  def validate(self, split_strings):
    checksum = 0
    for i in split_strings[:-2]:
      checksum += i
    return checksum % 256 == split_strings[15]
      
  def set_percentage(self, split_strings):
    self.percentage = split_strings[1]
    self.metrics.update_percentage(self.percentage)
    self._redis.publish('battery_percentage', self.percentage)
    print("percentage    :",self.percentage,"%")

  def set_voltage(self, split_strings):
    #self.voltage = int(f'0x{split_strings[2]:x}{split_strings[3]:x}',16)/100
    self.voltage = (split_strings[2]<<8 | split_strings[3])/100
    self.metrics.update_voltage(self.voltage)
    self._redis.publish('battery_voltage', self.voltage)
    print("voltage       :",self.voltage,"V")

  def set_capacity(self, split_strings):
    self.capacity = int('0x' + ''.join([format(c, '02X') for c in split_strings[4:8]]),16) / 1000
    self.metrics.update_capacity(self.capacity)
    self._redis.publish('battery_capacity', self.capacity)
    print("capacity      :",self.capacity,"Ah")

  def set_current(self, split_strings):
    self.current = int('0x' + ''.join([format(c, '02X') for c in split_strings[8:12]]),16)
    if self.current >= 0x80000000:
      self.current -= 0x100000000
    self.metrics.update_current(self.current)
    self._redis.publish('battery_current', self.current)
    print("current       :", self.current,"mA")

  
  def set_remaining_sec(self, split_strings):
    self.remaining_sec = int('0x' + ''.join([format(c, '02X') for c in split_strings[12:15]]),16)
    self.metrics.update_remaining_sec(self.remaining_sec)
    self._redis.publish('battery_remaining_sec', self.remaining_sec)
    print("remaining_sec :", self.remaining_sec,"s")

  def fetch_data(self):
    while True:
      split_strings = []
      try:
        newdata_hex=self.ser.readline().hex()
      except:
        pass

      while newdata_hex.startswith("a5") and len(newdata_hex) < 34:
        newdata_hex = ''.join((newdata_hex,self.ser.readline().hex()))
      
      for index in range(0,len(newdata_hex), 2):
        split_strings.append(int(newdata_hex[index : index + 2],16))

      if newdata_hex.startswith('a5') and len (newdata_hex) <= 34:
        if self.validate(split_strings):
          self.set_percentage(split_strings)
          self.set_voltage(split_strings)
          self.set_capacity(split_strings)
          self.set_current(split_strings)
          self.set_remaining_sec(split_strings)
          print()

app = flask.Flask(__name__)
battery = Battery()
@app.route('/', methods=['GET'])
def index():
  msg = {
      'percentage'    : battery.percentage,
      'voltage'       : battery.voltage,
      'capacity'      : battery.capacity,
      'current'       : battery.current,
      'remaining_sec' : battery.remaining_sec
  }
  return flask.jsonify(msg)

app.run(host='0.0.0.0', port=5000)


#sudo chmod 777 /dev/ttyS0
