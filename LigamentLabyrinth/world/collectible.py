"""Collectible entity that player can pick up."""
from world.entity import Entity
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world.player import Player

class Collectible(Entity):
    """Represents a collectible item in the game world."""
    
    def __init__(self, x: float, y: float, texture_id: int = 11) -> None:
        super().__init__(x, y, texture_id)
        
        self.collected: bool = False
    
    def check_collection(self, player: 'Player', collection_distance: float) -> bool:
        """Check if player is close enough to collect this item."""
        if self.collected:
            return False
        
        dist_squared = self.get_distance_squared_to_player(player)
        
        if dist_squared < collection_distance * collection_distance:
            self.collected = True
            return True
        return False