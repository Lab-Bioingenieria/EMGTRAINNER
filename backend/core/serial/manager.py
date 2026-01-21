"""
Serial Communication Manager
Handles low-level serial port communication with ESP32
"""
import serial
import serial.tools.list_ports
from typing import Optional


class SerialManager:
    """Low-level serial port manager"""
    
    def __init__(self, baudrate: int = 115200):
        self.baudrate = baudrate
        self.connection: Optional[serial.Serial] = None
        self.port: Optional[str] = None
    
    def find_device_port(self, identifier: str = "USB") -> Optional[str]:
        """
        Find serial port by identifier
        
        Args:
            identifier: String to search in port description
            
        Returns:
            Port device name or None
        """
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if identifier in port.description or identifier in str(port.hwid):
                return port.device
        return None
    
    def connect(self, port: Optional[str] = None) -> bool:
        """
        Connect to serial port
        
        Args:
            port: Specific port to connect to, or None to auto-detect
            
        Returns:
            True if connected successfully
        """
        try:
            if port is None:
                port = self.find_device_port()
            
            if port is None:
                raise Exception("No device port found")
            
            self.connection = serial.Serial(
                port=port,
                baudrate=self.baudrate,
                timeout=1
            )
            self.port = port
            return True
            
        except Exception as e:
            print(f"Error connecting to serial port: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close serial connection"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            self.connection = None
            self.port = None
    
    def is_connected(self) -> bool:
        """Check if serial port is connected"""
        return self.connection is not None and self.connection.is_open
    
    def read_line(self) -> Optional[str]:
        """
        Read one line from serial port
        
        Returns:
            Decoded line or None if error/no data
        """
        if not self.is_connected():
            return None
        
        try:
            line = self.connection.readline().decode('utf-8').strip()
            return line if line else None
        except Exception as e:
            print(f"Error reading from serial: {e}")
            return None
    
    def write_line(self, data: str) -> bool:
        """
        Write line to serial port
        
        Args:
            data: String to write
            
        Returns:
            True if successful
        """
        if not self.is_connected():
            return False
        
        try:
            self.connection.write(f"{data}\n".encode('utf-8'))
            return True
        except Exception as e:
            print(f"Error writing to serial: {e}")
            return False
