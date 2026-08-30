"""
Serial Communication Manager
Handles low-level serial port communication with ESP32
"""
import serial
import serial.tools.list_ports
from typing import Optional

# The U2D2 that drives the Dynamixel hand is an FTDI device. pyserial builds
# `description` from the USB product string ("USB <-> Serial Converter") and
# `hwid` from "USB VID:PID=0403:6014 ...", so neither one contains the text
# "FTDI"; only `manufacturer` and the vendor id identify it. Matching on the
# vendor id is what keeps the sensor off the robotic hand's bus.
FTDI_VENDOR_ID = 0x0403


def _list_serial_ports() -> list:
    """Enumerate serial ports. Isolated so tests can substitute a bus."""
    return list(serial.tools.list_ports.comports())


def _is_ftdi(port_info) -> bool:
    """True when the port is an FTDI adapter, i.e. the Dynamixel bus."""
    if getattr(port_info, "vid", None) == FTDI_VENDOR_ID:
        return True
    text = " ".join(
        value for value in (
            getattr(port_info, "description", None),
            getattr(port_info, "manufacturer", None),
            getattr(port_info, "hwid", None),
        ) if value
    ).upper()
    return "FTDI" in text


class SerialManager:
    """Low-level serial port manager"""
    
    def __init__(self, baudrate: int = 115200):
        self.baudrate = baudrate
        self.connection: Optional[serial.Serial] = None
        self.port: Optional[str] = None
    
    def find_device_port(
        self,
        identifier: str = "USB",
        excluded_identifiers: list = None,
        exclude_ftdi: bool = True,
    ) -> Optional[str]:
        """
        Find serial port by identifier
        
        Args:
            identifier: String to search in port description
            excluded_identifiers: List of strings to exclude (e.g. ['FTDI'])
            exclude_ftdi: Skip FTDI adapters, which belong to the hand
            
        Returns:
            Port device name or None
        """
        if excluded_identifiers is None:
            excluded_identifiers = []

        ports = _list_serial_ports()
        for port in ports:
            # The hand's bus is never a sensor candidate, whatever it is called.
            if exclude_ftdi and _is_ftdi(port):
                continue

            # Check exclusions first
            is_excluded = False
            for exclude in excluded_identifiers:
                if exclude in port.description or exclude in str(port.hwid):
                    is_excluded = True
                    break
            
            if is_excluded:
                continue

            # Check match
            if identifier in port.description or identifier in str(port.hwid):
                return port.device
        return None

    def autodetect_sensor_port(self) -> Optional[str]:
        """
        Find the ESP32 sensor, preferring its known USB-to-UART bridges before
        falling back to any non-FTDI serial device.
        """
        for identifier in ("Silicon", "CH340", "USB"):
            port = self.find_device_port(identifier=identifier)
            if port is not None:
                return port
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
                port = self.autodetect_sensor_port()
            
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
            raise e
    
    def disconnect(self) -> None:
        """Close serial connection"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            self.connection = None
            self.port = None
    
    def is_connected(self) -> bool:
        """Check if serial port is connected and physically present"""
        if self.connection is None or not self.connection.is_open:
            return False

        # Additional check: Verify the port still exists in the OS
        # This catches physical disconnections (unplugging USB)
        try:
            available_ports = [p.device for p in serial.tools.list_ports.comports()]
            if self.port not in available_ports:
                self.disconnect()
                return False
            return True
        except Exception:
            return False
    
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
