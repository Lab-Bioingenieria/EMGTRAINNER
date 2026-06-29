"""
Use case for executing a hand gesture.
"""
from typing import Dict, Any

from app.services.hand_service import HandService


class ExecuteGesture:
    """
    Use case for executing a predefined hand gesture.
    
    This use case coordinates the execution of gestures on the prosthetic hand.
    """
    
    def __init__(self, hand_service: HandService):
        self.hand_service = hand_service
    
    def execute(self, gesture_name: str) -> Dict[str, Any]:
        """
        Execute a gesture.
        
        Args:
            gesture_name: Name of the gesture to execute
            
        Returns:
            Dict with execution result
            
        Raises:
            RuntimeError: If hand is not initialized
            ValueError: If gesture is invalid
        """
        return self.hand_service.execute_gesture(gesture_name)
