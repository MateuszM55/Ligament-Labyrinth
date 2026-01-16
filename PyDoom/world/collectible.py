"""Collectible entity that player can pick up."""

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world.player import Player


class Collectible:
    """Represents a collectible sprite in the game world."""
    
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
            player: The player object
            
        Returns:
            Distance in world units
        """
        dx = player.x - self.x
        dy = player.y - self.y
        return math.sqrt(dx * dx + dy * dy)
    
    def check_collection(self, player: 'Player', collection_distance: float) -> bool:
        """Check if player is close enough to collect this item.
        
        Args:
            player: The player object
            collection_distance: Distance threshold for collection
            
        Returns:
            True if collected, False otherwise
        """
        if self.collected:
            return False
            
        distance = self.get_distance_to_player(player)
        if distance < collection_distance:
            self.collected = True
            return True
        return False
