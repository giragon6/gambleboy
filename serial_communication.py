import json

import serial


class SerialCommunication:
  def __init__(self, port: str, baud: int, timeout: float):
    self.port = port
    self.baud = baud
    self.timeout = timeout
    self.connection = None
    self.connected = False
    
  def connect(self) -> bool:
    """Establish serial connection to RP2350"""
    try:
      self.connection = serial.Serial(self.port, self.baud, timeout=self.timeout)
      self.connected = True
      print(f"Serial connection established on {self.port} at {self.baud} baud")
      return True
    except serial.SerialException as e:
      print(f"Failed to connect to {self.port}: {e}")
      self.connected = False
      return False
    except Exception as e:
      print(f"Unexpected error connecting to serial: {e}")
      self.connected = False
      return False
  
  def disconnect(self):
    """Close serial connection"""
    if self.connection and self.connection.is_open:
      self.connection.close()
      self.connected = False
      print("Serial connection closed")
  
  def send_data(self, data: str) -> bool:
    """Send raw string data to RP2350 with newline"""
    if not self.connected or not self.connection:
      print("No serial connection available")
      return False
    
    try:
      command_with_newline = data + '\n'
      self.connection.write(command_with_newline.encode('utf-8'))
      self.connection.flush()
      return True
    except Exception as e:
      print(f"Error sending data: {e}")
      return False
  
  def send_raw_command(self, command: str) -> bool:
    """Send raw command to RP2350 (alias for send_data)"""
    return self.send_data(command)
  
  def read_data(self) -> dict | None:
    """Read JSON data from RP2350"""
    if not self.connected or not self.connection:
      return None
    
    try:
      if self.connection.in_waiting > 0:
        line = self.connection.readline().decode('utf-8').strip()
        if line:
          return json.loads(line)
    except Exception as e:
      print(f"Error reading data: {e}")
    return None