"""
EMG Data Service
Business logic for EMG data processing and management
"""
from typing import Optional, Dict, Any
from datetime import datetime
from core.serial.manager import SerialManager


class EMGDataService:
    """Service for managing EMG data collection and processing"""
    
    def __init__(self):
        self.serial_manager = SerialManager(baudrate=115200)
        self.is_streaming = False
    
    def connect_to_device(self, port: Optional[str] = None) -> Dict[str, Any]:
        """
        Connect to ESP32 device
        
        Args:
            port: Optional specific port, auto-detects if None
            
        Returns:
            Connection result with status and details
        """
        success = self.serial_manager.connect(port)
        
        return {
            "success": success,
            "port": self.serial_manager.port if success else None,
            "message": "Connected successfully" if success else "Connection failed"
        }
    
    def disconnect_from_device(self) -> Dict[str, Any]:
        """
        Disconnect from ESP32 device
        
        Returns:
            Disconnection result
        """
        self.serial_manager.disconnect()
        self.is_streaming = False
        
        return {
            "success": True,
            "message": "Disconnected from device"
        }
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get current connection status
        
        Returns:
            Status information
        """
        is_connected = self.serial_manager.is_connected()
        
        return {
            "connected": is_connected,
            "port": self.serial_manager.port if is_connected else None,
            "baudrate": self.serial_manager.baudrate,
            "streaming": self.is_streaming
        }
    
    def parse_emg_line(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Parse CSV line from ESP32 into structured data
        
        Args:
            line: Raw CSV line from serial
            
        Returns:
            Parsed EMG data or None if invalid
        """
        try:
            # Skip headers and system messages
            if any(keyword in line for keyword in ['timestamp', 'SISTEMA', '=', 'CSV_START', 'EMG Devices']):
                return None
            
            parts = line.split(',')
            if len(parts) < 7:
                return None
            
            return {
                "timestamp": int(parts[0]),
                "session_time": int(parts[1]),
                "emg1": float(parts[2]),
                "emg2": float(parts[3]),
                "emg3": float(parts[4]),
                "movement_id": int(parts[5]),
                "movement_name": parts[6].strip(),
                "received_at": datetime.now().isoformat()
            }
            
        except (ValueError, IndexError) as e:
            print(f"Error parsing EMG line: {e}")
            return None
    
    def read_emg_sample(self) -> Optional[Dict[str, Any]]:
        """
        Read a single EMG data sample
        
        Returns:
            Parsed EMG data or None
        """
        if not self.serial_manager.is_connected():
            return None
        
        # Try reading up to 10 lines to find valid data
        for _ in range(10):
            line = self.serial_manager.read_line()
            if line:
                data = self.parse_emg_line(line)
                if data:
                    return data
        
        return None
    
    def start_streaming(self):
        """Mark streaming as active"""
        self.is_streaming = True
    
    def stop_streaming(self):
        """Mark streaming as inactive"""
        self.is_streaming = False


# Global service instance (singleton pattern)
emg_service = EMGDataService()
