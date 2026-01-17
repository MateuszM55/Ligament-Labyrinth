"""Collectible entity that player can pick up."""

import math
from typing import TYPE_CHECKING

from world.entity import Entity

if TYPE_CHECKING:
    from world.player import Player


class Collectible(Entity):
    """Represents a collectible item in the game world."""
    
    def __init__(self, x: float, y: float, texture_id: int = 11) -> None:
        """Initialize the collectible.
        
        Args:
            x: X position in world coordinates
            y: Y position in world coordinates
            texture_id: Texture ID for the sprite
        """
        super().__init__(x, y, texture_id)
        self.collected: bool = False
    
    
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
        
        dist_squared = self.get_distance_squared_to_player(player)
        
        if dist_squared < collection_distance * collection_distance:
            self.collected = True
            return True
        return False
