"""
EMG Data Service
Business logic for EMG data processing and management
"""
from typing import Optional, Dict, Any
from datetime import datetime
from core.serial.manager import SerialManager


from app.services.csv_service import csv_service

import threading
import time
import re

class EMGDataService:
    """Service for managing EMG data collection and processing"""
    
    def __init__(self):
        self.serial_manager = SerialManager(baudrate=115200)
        self.is_streaming = False
        self.current_patient_name = "Guest"
        self.current_label = "Rest"
        self._streaming_thread = None
    
    def set_session_info(self, name: str):
        """Update session metadata"""
        self.current_patient_name = name
        
    def set_current_label(self, label: str):
        """Update current movement label"""
        self.current_label = label

    # ... (connect, disconnect, get_connection_status methods remain same) ...
    def connect_to_device(self, port: Optional[str] = None) -> Dict[str, Any]:
        """
        Connect to ESP32 device
        
        Args:
            port: Optional specific port, auto-detects if None
            
        Returns:
            Connection result with status and details
        """
        try:
            success = self.serial_manager.connect(port)
            return {
                "success": success,
                "port": self.serial_manager.port if success else None,
                "message": "Connected successfully" if success else "Connection failed (Check if Serial Monitor is open)"
            }
        except Exception as e:
            return {
                "success": False,
                "port": None,
                "message": f"Connection error: {str(e)}"
            }
    
    def disconnect_from_device(self) -> Dict[str, Any]:
        """
        Disconnect from ESP32 device
        
        Returns:
            Disconnection result
        """
        self.stop_streaming() # Stop thread first
        self.serial_manager.disconnect()
        
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
            "streaming": self.is_streaming,
            "current_label": self.current_label
        }

    def parse_emg_line(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Parse CSV/Serial line from ESP32 into structured data
        Handles both comma-separated and space-separated formats.
        """
        try:
            # Skip headers/metadata
            if any(keyword in line for keyword in ['SISTEMA', '=', 'CSV_START', 'EMG Devices', 'CMD_ACK', '---']):
                return None
            
            # Clean and split by comma or whitespace
            line = line.strip()
            if not line:
                return None
                
            parts = re.split(r'[,\s]+', line)
            parts = [p for p in parts if p] # remove empty strings
            
            if not parts:
                return None

            data = {}
            
            # Determine if first part is timestamp (simple heuristic: > 1000000000 is likely epoch ms or similar)
            # ESP32 usually sends millis() which is small, or nothing. 
            # If backend needs absolute time, we should generate it here if strictly growing text isn't found.
            
            # For now, we assume ESP32 sends straight data values (Muscle Levels) as per user provided code.
            # We generate the timestamp on the backend to be safe.
            
            current_time_ms = int(time.time() * 1000)
            
            # Map values to emgX
            # We assume all parts are sensor values
            emg_values = []
            try:
                emg_values = [float(p) for p in parts]
            except ValueError:
                # If conversion fails, it might contain text, skip
                return None

            data = {
                "timestamp": current_time_ms,
                "name": self.current_patient_name,
                "label": self.current_label
            }
            
            # Add dynamic EMG columns
            for i, val in enumerate(emg_values):
                data[f"emg{i+1}"] = val

            # If valid data and streaming, write to CSV
            if self.is_streaming:
                # print(f"DEBUG: Writing row: {data}")
                csv_service.write_row(data)
                
            return data
            
        except Exception as e:
            print(f"DEBUG: Parse error for line '{line.strip()}': {e}")
            return None
    
    def read_emg_sample(self) -> Optional[Dict[str, Any]]:
        """
        Read a single EMG data sample.
        If streaming thread is active, we shouldn't steal reads from it.
        """
        if not self.serial_manager.is_connected():
            return None
        
        # If streaming, we can't easily read one line without race conditions
        # ideally we should cache the last value from the thread
        if self.is_streaming:
             # Basic implementation: try to grab one line but risk collision
             # For better architecture, the thread should update a 'latest_sample' var
             pass

        # Try reading up to 10 lines to find valid data
        for _ in range(10):
            line = self.serial_manager.read_line()
            if line:
                data = self.parse_emg_line(line)
                if data:
                    return data
        
        return None
    
    def _streaming_loop(self):
        """Background loop to continuously read serial data"""
        print("Starting background streaming loop...")
        while self.is_streaming and self.serial_manager.is_connected():
            try:
                line = self.serial_manager.read_line()
                if line:
                    self.parse_emg_line(line)
                else:
                    # Small sleep to prevent CPU hogging if no data
                    time.sleep(0.001)
            except Exception as e:
                print(f"Error in streaming loop: {e}")
                time.sleep(0.1)
        print("Streaming loop stopped.")

    def start_streaming(self, category: str = ""):
        """Mark streaming as active"""
        if self.is_streaming:
            return

        self.is_streaming = True
        self.serial_manager.write_line("START_SESSION")
        csv_service.start_new_session(patient_name=self.current_patient_name)
        
        # Start background thread
        self._streaming_thread = threading.Thread(target=self._streaming_loop, daemon=True)
        self._streaming_thread.start()
    
    def stop_streaming(self):
        """Mark streaming as inactive"""
        self.is_streaming = False
        try:
            self.serial_manager.write_line("STOP_SESSION")
        except:
            pass
            
        csv_service.stop_session()
        
        if self._streaming_thread:
            self._streaming_thread.join(timeout=1.0)
            self._streaming_thread = None


# Global service instance (singleton pattern)
emg_service = EMGDataService()
