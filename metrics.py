import prometheus_client

class Metrics:
  def __init__(self, interval_seconds=0):   
    self.percentage = prometheus_client.Gauge("battery_percentage", "Battery percentage")
    self.voltage = prometheus_client.Gauge("battery_voltage", "Battery voltage")
    self.capacity = prometheus_client.Gauge("battery_capacity", "Battery capacity")
    self.current = prometheus_client.Gauge("battery_current", "Battery current")
    self.remaining_sec = prometheus_client.Gauge("battery_remaining_second", "Battery remaining seconds")

    prometheus_client.start_http_server(9090)

  def update_percentage(self, number):
    self.percentage.set(number)

  def update_voltage(self, number):
    self.voltage.set(number)

  def update_capacity(self, number):
    self.capacity.set(number)

  def update_current(self, number):
    self.current.set(number)

  def update_remaining_sec(self, number):
    self.remaining_sec.set(number)
