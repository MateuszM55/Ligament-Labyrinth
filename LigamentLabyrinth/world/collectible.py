"""Collectible entity that player can pick up."""

import math
from typing import TYPE_CHECKING

from world.entity_utils import distance_to_player, distance_squared_to_player

if TYPE_CHECKING:
    from world.player import Player


class Collectible:
    """Represents a collectible item in the game world."""
    
    def __init__(self, x: float, y: float, texture_id: int = 11) -> None:
        """Initialize the collectible.
        
        Args:
            x: X position in world coordinates
            y: Y position in world coordinates
            texture_id: Texture ID for the sprite
        """
        self.x: float = float(x)
        self.y: float = float(y)
        self.texture_id: int = texture_id
        self.collected: bool = False
    
    def get_distance_to_player(self, player: 'Player') -> float:
        """Calculate distance from collectible to player.
        
        Args:
            player: Player object
            
        Returns:
            Distance in world units
        """
        return distance_to_player(self.x, self.y, player)
    
    def get_distance_squared_to_player(self, player: 'Player') -> float:
        """Calculate squared distance from collectible to player (faster, no sqrt).
        
        Args:
            player: Player object
            
        Returns:
            Squared distance in world units
        """
        return distance_squared_to_player(self.x, self.y, player)
    
    
    def check_collection(self, player: 'Player', collection_distance: float) -> bool:
        """Check if player is close enough to collect this item.
        
        Args:
            player: Player object
            collection_distance: Distance threshold for collection
            
        Returns:
            True if item was collected, False otherwise
        """
        if self.collected:
            return False
        
        # Use squared distance to avoid expensive sqrt
        if self.get_distance_squared_to_player(player) < collection_distance ** 2:
            self.collected = True
            return True
        return False
