"""Base entity class for objects in the game world."""
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world.player import Player


class Entity:
    """Base class for any dynamic object in the world."""
    
    def __init__(self, x: float, y: float, texture_id: int) -> None:
        """Initialize a new entity.

        Args:
            x: Initial X position.
            y: Initial Y position.
            texture_id: The ID of the texture used for rendering this entity.
        """
        self.x: float = float(x)
        self.y: float = float(y)
        self.texture_id: int = int(texture_id)
        self.active: bool = True
    
    def get_distance_to_player(self, player: 'Player') -> float:
        """Calculate the Euclidean distance to the player.

        Args:
            player: The player instance.

        Returns:
            The distance to the player (uses sqrt).
        """
        return math.hypot(player.x - self.x, player.y - self.y)
    
    def get_distance_squared_to_player(self, player: 'Player') -> float:
        """Calculate the squared distance to the player.

        Args:
            player: The player instance.

        Returns:
            The squared distance to the player (faster than get_distance_to_player).
        """
        dx = player.x - self.x
        dy = player.y - self.y
        return dx * dx + dy * dy
    
    def update(self, dt: float, player: 'Player') -> None:
        """Update the entity's state. Override in subclasses.
        
        Args:
            dt: Delta time in seconds.
            player: The player instance.
        """
        pass
    
    @property
    def render_data(self) -> tuple[float, float, int]:
        """Get the data needed for rendering this entity.
        
        Returns:
            Tuple of (x, y, texture_id) for use in sprite rendering.
        """
        return (self.x, self.y, self.texture_id)
