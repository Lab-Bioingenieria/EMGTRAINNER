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
import asyncio

# Hand Control Imports
from hand.core.dynamixel_interface import DynamixelInterface, find_u2d2_port
from hand.control.hand_controller import execute_gesture
from hand.models.hand_profiles import ELEVEN_DOF_RIGHT

from app.utils.umyo import umyo_parser
from app.services.websocket_manager import websocket_manager

class EMGDataService:
    """Service for managing EMG data collection and processing"""
    
    def __init__(self):
        self.serial_manager = SerialManager(baudrate=921600)
        self.is_streaming = False
        self.current_patient_name = "Guest"
        self.current_patient_age = None
        self.current_label = "Rest"
        self._streaming_thread = None
        self.loop = None

        # uMyo processing state
        self.last_data_upd = 0
        self.parse_unproc_cnt = 0
        self.ch0 = 0
        self.ch1 = 0
        self.ch2 = 0
        self.avg0 = 0
        self.avg1 = 0
        self.avg2 = 0

        # Hand Interface
        self.hand_interface = None
        self.hand_profile = ELEVEN_DOF_RIGHT
        
        # Try to connect hand on startup (non-blocking if possible, but U2D2 init is fast)
        self.connect_hand()

    def connect_hand(self):
        """Initialize Dynamixel Hand connection"""
        try:
            port = find_u2d2_port()
            if port:
                self.hand_interface = DynamixelInterface(port_name=port)
                self.hand_interface.initialize()
                ids = self.hand_interface.scan_motors()
                print(f"[INFO] - Hand connected on {port}. Motors: {ids}")
            else:
                print("[WARN] - Hand not found (U2D2)")
        except Exception as e:
            print(f"[ERROR] - Hand connection failed: {e}")
            self.hand_interface = None

    def set_session_info(self, name: str, age: Optional[str] = None):
        """Update session metadata"""
        # Clean inputs to avoid CSV issues
        self.current_patient_name = name.replace(',', '') if name else "Guest"
        self.current_patient_age = age.replace(',', '') if age else ""
        
    def set_current_label(self, label: str):
        """Update current movement label and trigger hand gesture"""
        if self.current_label == label:
            return

        self.current_label = label
        
        # Trigger Hand Movement if connected
        if self.hand_interface:
            # Map frontend labels to backend gestures if needed
            gesture_name = label.upper()
            
            # Simple Mapping for common mismatches and Spanish frontend labels
            mapping = {
                "ABRIR": "ZERO",      # User requested OPEN -> ZERO
                "CERRAR": "CLOSE",
                "LIKE": "LIKE",
                "APUNTAR": "POINT",
                "PINZA": "PINCH",
                "CILINDRICO": "CYLINDRICAL",
                "ESFÉRICO": "BALL",   # User requested SPHERICAL -> BALL
                "ESFERICO": "BALL",   # Fail-safe
                "REST": "REST",
                
                # English Fallbacks just in case
                "OPEN": "ZERO",
                "GLOSE": "CLOSE",
                "POINT": "POINT",
                "PINCH": "PINCH", 
                "CYLINDRICAL": "CYLINDRICAL",
                "SPHERICAL": "BALL",
                "BALL": "BALL",
                "ZERO": "ZERO"
            }
            
            if gesture_name in mapping:
                gesture_name = mapping[gesture_name]
            
            # Run in background to avoid blocking API
            threading.Thread(target=self._move_hand, args=(gesture_name,), daemon=True).start()

    def _move_hand(self, gesture_name: str):
        """Execute gesture on the hand safely"""
        try:
            print(f"[HAND] Executing gesture: {gesture_name}")
            execute_gesture(self.hand_interface, self.hand_profile, gesture_name)
        except Exception as e:
            print(f"[HAND] Error executing {gesture_name}: {e}")

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
            # We explicitly want to avoid FTDI ports for the sensor (ESP32)
            # because FTDI is likely the Dynamixel Hand.
            # If the user passed a specific port, we respect it.
            # If auto-detecting (port=None), we pass logic to manager or handle exclusion here.
            # The manager's connect() method has been updated to try smart detection excluding FTDI.
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

            # Construct data with Spanish keys as requested for CSV output
            # User request: nombre,edad,emg1,emg2,emg3,labels
            data = {
                "nombre": self.current_patient_name,
                "edad": self.current_patient_age if self.current_patient_age else "",
                # "timestamp": current_time_ms, # Removed timestamp from direct CSV dict to follow user strict format
                "labels": self.current_label
            }
            
            # Add dynamic EMG columns
            # Ensure we have at least 3 for consistency if possible, or just what we receive
            for i, val in enumerate(emg_values):
                data[f"emg{i+1}"] = val
            
            # If we received fewer than 3, maybe pad? 
            # The prompt implies fixed emg1,emg2,emg3. 
            # If the device sends fewer, we might have issues. 
            # Assuming device sends 3. If not, this loop handles what is there.
            
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
        
        # Reset state
        self.parse_unproc_cnt = 0
        self.ch0 = 0
        self.ch1 = 0
        self.ch2 = 0
        self.avg0 = 0
        self.avg1 = 0
        self.avg2 = 0
        
        buffer = b""

        while self.is_streaming and self.serial_manager.is_connected():
            try:
                conn = self.serial_manager.connection
                if not conn:
                    break

                cnt = conn.in_waiting
                if cnt > 0:
                    data = conn.read(cnt)
                    
                    # 1. Try uMyo Parser (Binary)
                    self.parse_unproc_cnt = umyo_parser.umyo_parse_preprocessor(data)
                    umyos = umyo_parser.umyo_get_list()
                    num_sensors = len(umyos)
                    
                    if num_sensors > 0:
                        # --- BINARY/uMyo LOGIC ---
                        # Process sensor data (User logic)
                        val0 = (umyos[0].device_spectr[2] + umyos[0].device_spectr[3]) if num_sensors > 0 else 0
                        val1 = (umyos[1].device_spectr[2] + umyos[1].device_spectr[3]) if num_sensors > 1 else 0
                        val2 = (umyos[2].device_spectr[2] + umyos[2].device_spectr[3]) if num_sensors > 2 else 0

                        self.ch0 = self.ch0 * 0.8 + 0.2 * val0
                        self.ch1 = self.ch1 * 0.8 + 0.2 * val1
                        self.ch2 = self.ch2 * 0.8 + 0.2 * val2
                        
                        scale = 1
                        T = 300
                        
                        # Normalization
                        denominator = (self.ch0 + self.ch1 + self.ch2 + T)
                        if denominator == 0: denominator = 1
                        
                        dc0 = (self.ch0 / denominator * scale) if num_sensors > 0 else ""
                        dc1 = (self.ch1 / denominator * scale) if num_sensors > 1 else ""
                        dc2 = (self.ch2 / denominator * scale) if num_sensors > 2 else ""
                        
                        # Broadcast
                        payload = {"dc0": dc0 if dc0 != "" else 0, "dc1": dc1 if dc1 != "" else 0, "dc2": dc2 if dc2 != "" else 0}
                        if self.loop:
                            asyncio.run_coroutine_threadsafe(websocket_manager.broadcast(payload), self.loop)

                        # CSV Write
                        csv_data = {
                            "nombre": self.current_patient_name,
                            "edad": self.current_patient_age if self.current_patient_age else "",
                            "labels": self.current_label,
                            "emg1": dc0,
                            "emg2": dc1,
                            "emg3": dc2
                        }
                        csv_service.write_row(csv_data)
                        print(f"EMG (Bin): {dc0}, {dc1}, {dc2} | {self.current_label}", flush=True)

                    else:
                        # --- TEXT LOGIC (Fallback) ---
                        # If uMyo didn't pick it up, maybe it's simple text lines
                        buffer += data
                        
                        # Process complete lines
                        while b'\n' in buffer:
                            line_data, buffer = buffer.split(b'\n', 1)
                            try:
                                line_str = line_data.decode('utf-8', errors='ignore').strip()
                                if not line_str: continue
                                
                                # parse_emg_line handles processing and CSV writing
                                parsed_data = self.parse_emg_line(line_str)
                                
                                if parsed_data:
                                    # Broadcast what we parsed
                                    # extract raw values or assume they are normalized? 
                                    # Usually text send raw, so we might want to normalize here too?
                                    # For now, just pass them through as "dc" values
                                    
                                    v1 = parsed_data.get("emg1", 0)
                                    v2 = parsed_data.get("emg2", 0)
                                    v3 = parsed_data.get("emg3", 0)
                                    
                                    payload = {"dc0": v1, "dc1": v2, "dc2": v3}
                                    if self.loop:
                                        asyncio.run_coroutine_threadsafe(websocket_manager.broadcast(payload), self.loop)
                                        
                                    print(f"EMG (Txt): {v1}, {v2}, {v3} | {self.current_label}", flush=True)

                            except Exception as e:
                                print(f"Text parse error: {e}")
                                
                else:
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
        
        # Try to get the running loop
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            print("Warning: Could not get running loop for websocket broadcast")
            self.loop = None

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
