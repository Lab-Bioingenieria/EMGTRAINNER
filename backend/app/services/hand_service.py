"""
Hand Service - Integrated with backend architecture

This service provides a unified interface for hand control operations,
following the same patterns as other services in the backend.
"""
import os
from typing import Optional, Dict, List, Any
from datetime import datetime

from hand.core.dynamixel_interface import DynamixelInterface
from hand.control.hand_controller import initialize_hand_profile, execute_gesture
from hand.models.hand_profiles import HAND_PROFILES, HandProfile
from hand.models.gestures import GESTURES


class HandService:
    """
    Service for controlling the prosthetic hand.
    
    This service follows the singleton pattern for the hardware interface
    and provides methods for initialization, gesture execution, and status reporting.
    """
    
    _instance: Optional['HandService'] = None
    _dx: Optional[DynamixelInterface] = None
    
    def __init__(self):
        self._profile: Optional[HandProfile] = None
        self._initialized: bool = False
        self._initialized_at: Optional[datetime] = None
        
    @classmethod
    def get_instance(cls) -> 'HandService':
        """Get or create the singleton instance of HandService."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @property
    def dx(self) -> Optional[DynamixelInterface]:
        """Get the Dynamixel interface instance."""
        if self._dx is None and self._initialized:
            # Lazy initialization of hardware interface
            port = os.getenv(
                "DYNAMIXEL_PORT",
                "/dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_FTAO520W-if00-port0"
            )
            try:
                self._dx = DynamixelInterface(port_name=port)
            except RuntimeError:
                pass  # Hardware not available, will be handled by initialize_hand
        return self._dx
    
    @property
    def profile(self) -> Optional[HandProfile]:
        """Get the current hand profile."""
        return self._profile
    
    @property
    def is_initialized(self) -> bool:
        """Check if the hand service is initialized."""
        return self._initialized
    
    def initialize_hand(self, profile_name: str) -> Dict[str, Any]:
        """
        Initialize the hand with a specific profile.
        
        Args:
            profile_name: Name of the hand profile to use
            
        Returns:
            Dict with initialization status and details
            
        Raises:
            ValueError: If the profile name is invalid
            RuntimeError: If hardware initialization fails
        """
        if profile_name not in HAND_PROFILES:
            raise ValueError(f"Perfil de mano no válido: {profile_name}")
        
        self._profile = HAND_PROFILES[profile_name]
        
        # Initialize hardware
        if self._dx is None:
            port = os.getenv(
                "DYNAMIXEL_PORT",
                "/dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_FTAO520W-if00-port0"
            )
            self._dx = DynamixelInterface(port_name=port)
        
        self._dx.initialize()
        self._dx.scan_motors()
        initialize_hand_profile(self._dx, self._profile)
        
        self._initialized = True
        self._initialized_at = datetime.utcnow()
        
        return {
            "status": "initialized",
            "profile_name": profile_name,
            "detected_motors": self._dx.detected_ids,
            "timestamp": self._initialized_at.isoformat()
        }
    
    def execute_gesture(self, gesture_name: str) -> Dict[str, Any]:
        """
        Execute a predefined gesture.
        
        Args:
            gesture_name: Name of the gesture to execute
            
        Returns:
            Dict with execution status
            
        Raises:
            RuntimeError: If the hand is not initialized
            ValueError: If the gesture is invalid
        """
        if not self._initialized or self._profile is None:
            raise RuntimeError("La mano no ha sido inicializada")
        
        if self._dx is None:
            raise RuntimeError("Interfaz de hardware no disponible")
        
        execute_gesture(self._dx, self._profile, gesture_name)
        
        return {
            "status": "executed",
            "gesture_name": gesture_name,
            "profile_name": self._profile.name,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the hand service.
        
        Returns:
            Dict with detailed status information
        """
        status = {
            "is_initialized": self._initialized,
            "profile_name": self._profile.name if self._profile else None,
            "initialized_at": self._initialized_at.isoformat() if self._initialized_at else None,
            "detected_motors": [],
            "motors_status": []
        }
        
        if self._dx and self._initialized:
            status["detected_motors"] = self._dx.detected_ids
            
            # Get motor status for detected motors
            for motor_id in self._dx.detected_ids:
                try:
                    position = self._dx.read_position(motor_id)
                    current = self._dx.read_current_amps(motor_id)
                    status["motors_status"].append({
                        "motor_id": motor_id,
                        "current_position": position,
                        "current_amps": current,
                        "is_enabled": True
                    })
                except Exception:
                    status["motors_status"].append({
                        "motor_id": motor_id,
                        "current_position": 0,
                        "current_amps": 0.0,
                        "is_enabled": False
                    })
        
        return status
    
    def get_available_profiles(self) -> List[str]:
        """Get list of available hand profiles."""
        return list(HAND_PROFILES.keys())
    
    def get_available_gestures(self, profile_name: Optional[str] = None) -> List[str]:
        """
        Get list of available gestures.
        
        Args:
            profile_name: Optional profile name to filter gestures
            
        Returns:
            List of gesture names
        """
        if profile_name:
            # Filter gestures that support this profile
            return [
                gesture for gesture, profiles in GESTURES.items()
                if profile_name in profiles
            ]
        return list(GESTURES.keys())
    
    def reset(self) -> None:
        """Reset the hand service state."""
        self._profile = None
        self._initialized = False
        self._initialized_at = None
        # Note: We don't close the hardware interface here to allow re-initialization


# Singleton instance for dependency injection
hand_service = HandService.get_instance()
