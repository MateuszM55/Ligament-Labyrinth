"""Base entity class for objects in the game world."""
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world.player import Player

class Entity:
    """Base class for any dynamic object in the world."""
    
    def __init__(self, x: float, y: float, texture_id: int) -> None:
        self.x: float = float(x)
        self.y: float = float(y)
        self.texture_id: int = int(texture_id)
    
    def get_distance_to_player(self, player: 'Player') -> float:
        """Calculate exact distance (Expensive: uses sqrt)."""
        return math.hypot(player.x - self.x, player.y - self.y)
    
    def get_distance_squared_to_player(self, player: 'Player') -> float:
        """Calculate distance squared (Fast: for collisions)."""
        dx = player.x - self.x
        dy = player.y - self.y
        return dx * dx + dy * dy