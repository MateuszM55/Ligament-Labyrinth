"""Monster entity that always faces the player."""

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world.player import Player


class Monster:
    """Represents a monster/enemy sprite in the game world."""
    
    def __init__(self, x: float, y: float, texture_id: int = 0) -> None:
        """Initialize the monster.
        
        Args:
            x: X position in world coordinates
            y: Y position in world coordinates
            texture_id: Texture ID for the sprite
        """
        self.x: float = float(x)
        self.y: float = float(y)
        self.texture_id: int = texture_id
        
    def get_angle_to_player(self, player: 'Player') -> float:
        """Calculate the angle from monster to player (for billboarding).
        
        Args:
            player: The player object
            
        Returns:
            Angle in radians
        """
        dx = player.x - self.x
        dy = player.y - self.y
        return math.atan2(dy, dx)
    
    def get_distance_to_player(self, player: 'Player') -> float:
        """Calculate distance from monster to player.
        
        Args:
            player: The player object
            
        Returns:
            Distance in world units
        """
        dx = player.x - self.x
        dy = player.y - self.y
        return math.sqrt(dx * dx + dy * dy)
