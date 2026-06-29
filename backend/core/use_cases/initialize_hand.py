"""
Use case for initializing the hand with a profile.
"""
from typing import Dict, Any

from app.services.hand_service import HandService


class InitializeHand:
    """
    Use case for initializing the prosthetic hand.
    
    This use case coordinates the initialization of the hand hardware
    with a specific profile configuration.
    """
    
    def __init__(self, hand_service: HandService):
        self.hand_service = hand_service
    
    def execute(self, profile_name: str) -> Dict[str, Any]:
        """
        Execute the hand initialization.
        
        Args:
            profile_name: Name of the hand profile to use
            
        Returns:
            Dict with initialization result
            
        Raises:
            ValueError: If profile is invalid
            RuntimeError: If hardware initialization fails
        """
        return self.hand_service.initialize_hand(profile_name)
