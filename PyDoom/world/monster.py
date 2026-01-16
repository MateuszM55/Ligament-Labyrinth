"""Monster entity that always faces the player."""

import math
from typing import TYPE_CHECKING

from settings import settings

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
    
    def move_towards_player(self, player: 'Player', dt: float) -> None:
        """Move the monster towards the player, ignoring walls.
        
        Args:
            player: The player object
            dt: Delta time in seconds
        """
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            move_speed = settings.monster.move_speed * dt
            normalized_dx = (dx / distance) * move_speed
            normalized_dy = (dy / distance) * move_speed
            
            self.x += normalized_dx
            self.y += normalized_dy
