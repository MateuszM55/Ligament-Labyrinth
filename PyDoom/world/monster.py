"""Monster entity that chases the player."""

import math
from typing import TYPE_CHECKING

from settings import settings
from world.entity_utils import distance_to_player, distance_squared_to_player

if TYPE_CHECKING:
    from world.player import Player


class Monster:
    """Represents a monster/enemy sprite that chases the player."""
    
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
        self.speed_multiplier: float = 1.0
    
    def get_distance_to_player(self, player: 'Player') -> float:
        """Calculate distance from monster to player.
        
        Args:
            player: Player object
            
        Returns:
            Distance in world units
        """
        return distance_to_player(self.x, self.y, player)
    
    def get_distance_squared_to_player(self, player: 'Player') -> float:
        """Calculate squared distance from monster to player (faster, no sqrt).
        
        Args:
            player: Player object
            
        Returns:
            Squared distance in world units
        """
        return distance_squared_to_player(self.x, self.y, player)
    
    
    def move_towards_player(self, player: 'Player', dt: float) -> None:
        """Move the monster towards the player (ignores walls).
        
        Args:
            player: Player object
            dt: Delta time in seconds
        """
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            # Normalize direction and apply speed
            move_speed = settings.monster.move_speed * self.speed_multiplier * dt
            self.x += (dx / distance) * move_speed
            self.y += (dy / distance) * move_speed

