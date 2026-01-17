"""Base entity class for objects in the game world."""

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world.player import Player


class Entity:
    """Base class for any object in the world with a position and texture."""
    
    def __init__(self, x: float, y: float, texture_id: int) -> None:
        """Initialize the entity.
        
        Args:
            x: X position in world coordinates
            y: Y position in world coordinates
            texture_id: Texture ID for the sprite
        """
        self.x: float = float(x)
        self.y: float = float(y)
        self.texture_id: int = texture_id
    
    def get_distance_to_player(self, player: 'Player') -> float:
        """Calculate distance from entity to player.
        
        Args:
            player: Player object
            
        Returns:
            Distance in world units
        """
        return math.hypot(player.x - self.x, player.y - self.y)
    
    def get_distance_squared_to_player(self, player: 'Player') -> float:
        """Calculate squared distance from entity to player (faster, no sqrt).
        
        Args:
            player: Player object
            
        Returns:
            Squared distance in world units
        """
        dx = player.x - self.x
        dy = player.y - self.y
        return dx * dx + dy * dy
